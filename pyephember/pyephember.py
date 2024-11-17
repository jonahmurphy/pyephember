"""
PyEphEmber interface implementation for https://ember.ephcontrols.com/
"""
# pylint: disable=consider-using-f-string

import base64
import datetime
import json
import time
import collections

from enum import Enum

import requests
import paho.mqtt.client as mqtt


class ZoneMode(Enum):
    """
    Modes that a zone can be set too
    """
    # pylint: disable=invalid-name
    AUTO = 0
    ALL_DAY = 1
    ON = 2
    OFF = 3

def zone_is_target_temperature_reached(zone):
    return zone_current_temperature(zone) >= zone_target_temperature(zone)

def zone_is_target_boost_temperature_reached(zone):
    return zone_boost_temperature(zone) >= zone_target_temperature(zone)

def zone_is_active(zone):
    """
    Check if the zone is on.
    This is a bit of a hack as the new API doesn't have a currently
    active variable
    """
    # not sure how accurate the following tests are
    if (zone_is_scheduled_on(zone) or zone_advance_active(zone)) and not zone_is_target_temperature_reached(zone):
        return True
    if zone_boost_hours(zone) > 0 and not zone_is_target_boost_temperature_reached(zone):
        return True

    return False

def zone_advance_active(zone):
    """
    Check if zone has advance active
    """
    return zone.get('isadvanceactive', False)
    #return zone_pointdata_value(zone, 'ADVANCE_ACTIVE') != 0

def boiler_state(zone):
    """
    Return the boiler state for a zone, as given by the API
    Probable interpretation:
    0 => FIXME, 1 => flame off, 2 => flame on
    
    boilerstate is not available in the latest API 
    """
    raise NotImplemented("boiler_state not implemented")
    #return zone_pointdata_value(zone, 'BOILER_STATE')

def zone_is_scheduled_on(zone):
    """
    Check if zone is scheduled to be on
    """
    mode = zone_mode(zone)
    if mode == ZoneMode.OFF:
        return False

    if mode == ZoneMode.ON:
        return True

    def scheduletime_to_time(stime):
        """
        Convert from string time in format 12:30
        to python datetime
        """
        time_str = '13::55::26'
        return datetime.datetime.strptime(stime, '%H:%M').time()

    zone_tstamp = time.gmtime(zone['timestamp']/1000)
    zone_ts_time = datetime.time(zone_tstamp.tm_hour, zone_tstamp.tm_min)
  
    for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        program = zone['programmes'][day]
        if mode == ZoneMode.AUTO:
            for period in ['p1', 'p2', 'p3']:
                start_time = scheduletime_to_time(program[period]['starttime'])
                end_time = scheduletime_to_time(program[period]['endtime'])
                if start_time <= zone_ts_time <= end_time:
                    return True
        elif mode == ZoneMode.ALL_DAY:
            start_time = scheduletime_to_time(program['p1']['starttime'])
            end_time = scheduletime_to_time(program['p3']['endtime'])
            if start_time <= zone_ts_time <= end_time:
                return True
    return False

def zone_name(zone):
    """
    Get zone name
    """
    return zone["name"]

def zone_is_boost_active(zone):
    """
    Is the boost active for the zone
    """
    return zone.get('isboostactive', False)

def zone_boost_hours(zone):
    """
    Return zone boost hours
    """
    if not zone_is_boost_active(zone):
        return 0
    boost_activations = _zone_boostactivation(zone)
    if not boost_activations:
        return 0
    return boost_activations.get('numberofhours', 0)

def zone_boost_timestamp(zone):
    """
    Return zone boost hours
    """
    if not zone_is_boost_active(zone):
        return None
    boost_activations = _zone_boostactivation(zone)
    if not boost_activations:
        return None
    return boost_activations.get('activatedon', None)

def zone_boost_temperature(zone):
    """
    Get target temperature for this zone
    """
    boost_activation = _zone_boostactivation(zone)
    if boost_activation is None:
        return None
    return boost_activation.get('targettemperature', None)

def zone_target_temperature(zone):
    """
    Get target temperature for this zone
    """
    return zone.get('targettemperature', None)

def zone_current_temperature(zone):
    """
    Get current temperature for this zone
    """
    return zone.get('currenttemperature', None)

def zone_mode(zone):
    """
    Get mode for this zone
    """
    return ZoneMode(zone.get('mode', None))

def zone_is_hot_water(zone):
    return zone.get('ishotwater', False)

def _zone_boostactivation(zone):
    return zone.get('boostActivations', None)

class EphEmber:
    """
    Interacts with a EphEmber thermostat via API.
    Example usage: t = EphEmber('me@somewhere.com', 'mypasswd')
                   t.get_zone_temperature('myzone') # Get temperature
    """

    # pylint: disable=too-many-public-methods

    def _http(self, endpoint, *, method=requests.post, headers=None,
              send_token=False, data=None, timeout=10):
        """
        Send a request to the http API endpoint
        method should be requests.get or requests.post
        """
        if not headers:
            headers = {}

        if send_token:
            if not self._do_auth():
                raise RuntimeError("Unable to login")
            headers["Authorization"] = self._login_data["data"]["token"]
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"

        url = "{}{}".format(self.http_api_base, endpoint)

        if data and isinstance(data, dict):
            data = json.dumps(data)

        response = method(url, data=data, headers=headers, timeout=timeout)

        if response.status_code != 200:
            raise RuntimeError(
                "{} response code.".format(response.status_code)
            )

        return response

    def _requires_refresh_token(self):
        """
        Check if a refresh of the token is needed
        """
        expires_on = self._login_data["last_refresh"] + \
            datetime.timedelta(seconds=self._refresh_token_validity_seconds)
        refresh = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        return expires_on < refresh

    def _request_token(self, force=False):
        """
        Request a new auth token
        """
        if self._login_data is None:
            raise RuntimeError("Don't have a token to refresh")

        if not force:
            if not self._requires_refresh_token():
                # no need to refresh as token is valid
                return True

        response = self._http(
            "appLogin/refreshAccessToken",
            method=requests.get,
            headers={'Authorization':
                     self._login_data['data']['refresh_token']}
        )

        refresh_data = response.json()

        if 'token' not in refresh_data.get('data', {}):
            return False

        self._login_data['data'] = refresh_data['data']
        self._login_data['last_refresh'] = datetime.datetime.utcnow()

        return True

    def _login(self):
        """
        Login using username / password and get the first auth token
        """
        self._login_data = None

        response = self._http(
            "appLogin/login",
            data={
                'userName': self._user['username'],
                'password': self._user['password']
            }
        )

        self._login_data = response.json()
        if self._login_data['status'] != 0:
            self._login_data = None
            return False
        self._login_data["last_refresh"] = datetime.datetime.utcnow()

        if ('data' in self._login_data
                and 'token' in self._login_data['data']):
            return True

        self._login_data = None
        return False

    def _do_auth(self):
        """
        Do authentication to the system (if required)
        """
        if self._login_data is None:
            return self._login()

        return self._request_token()

    def _get_user_details(self):
        """
        Get user details [user/selectUser]
        """
        response = self._http(
            "user/selectUser", method=requests.get,
            send_token=True
        )
        user_details = response.json()
        if user_details['status'] != 0:
            return {}
        return user_details

    def _get_user_id(self, force=False):
        """
        Get user ID
        """
        if not force and self._user['user_id']:
            return self._user['user_id']

        user_details = self._get_user_details()
        data = user_details.get('data', {})
        if 'id' not in data:
            raise RuntimeError("Cannot get user ID")
        self._user['user_id'] = str(data['id'])
        return self._user['user_id']

    def _get_first_gateway_id(self):
        """
        Get the first gatewayid associated with the account
        """
        if not self._homes:
            raise RuntimeError("Cannot get gateway id from list of homes.")
        return self._homes[0]['gatewayid']

    def _set_zone_target_temperature(self, zone, target_temperature):
        response = self._http(
            "zones/setTargetTemperature", method=requests.post,
            send_token=True,
            data={"temperature": target_temperature, "zoneid": zone['zoneid']}
        )
        
    def _set_zone_advance(self, zone, advance=True):
        if advance:
            self._http(
                "zones/adv", method=requests.post,
                send_token=True,
                data={"zoneid": zone['zoneid']}
            )  
        else:
            self._http(
                "zones/cancelAdv", method=requests.post,
                send_token=True,
                data={"zoneid": zone['zoneid']}
            )  
             

    def _set_zone_boost(self, zone, boost_temperature, num_hours):
        """
        Internal method to set zone boost

        num_hours should be 0, 1, 2 or 3
        """
        self._http(
            "zones/boost", method=requests.post,
            send_token=True,
            data={"hours": num_hours, "temperature": boost_temperature, "zoneid": zone['zoneid']}
        )   
        
    def _cancel_zone_boost(self, zone):
        self._http(
            "zones/cancelBoost", method=requests.post,
            send_token=True,
            data={"zoneid": zone['zoneid']}
        )   

    def _set_zone_mode(self, zone, mode_num):
        """
        Change the mode using the "mode" api.
        
        Seems likely that this may change, given the type in the endpoint name payload
        """
        self._http(
            "zones/setModel", method=requests.post,
            send_token=True,
            data={"zoneid": zone['zoneid'], "model": mode_num}
        )   

    # Public interface

    def list_homes(self):
        """
        List the homes available for this user
        """
        response = self._http(
            "homes/list", method=requests.get, send_token=True
        )
        homes = response.json()
        status = homes.get('status', 1)
        if status != 0:
            raise RuntimeError("Error getting home: {}".format(status))

        return homes.get("data", [])

    def get_home_details(self, gateway_id=None, force=False):
        """
        Get the details about a home (API call: homes/detail)
        If no gateway_id is passed, the first gateway found is used.
        """
        if self._home_details and not force:
            return self._home_details

        if gateway_id is None:
            if not self._homes:
                self._homes = self.list_homes()
            gateway_id = self._get_first_gateway_id()

        response = self._http(
            "homes/detail", send_token=True,
            data={"gateWayId": gateway_id}
        )

        home_details = response.json()

        status = home_details.get('status', 1)
        if status != 0:
            raise RuntimeError(
                "Error getting details from home: {}".format(status))

        if "data" not in home_details or "homes" not in home_details["data"]:
            raise RuntimeError(
                "Error getting details from home: no home data found")

        self._home_details = home_details['data']
        print("home details")
        print(home_details)
        return home_details["data"]

    def get_home(self, gateway_id=None):
        """
        Get the data about a home (API call: zones/polling).
        If no gateway_id is passed, the first gateway found is used.
        """
        if gateway_id is None:
            if not self._homes:
                self._homes = self.list_homes()
            gateway_id = self._get_first_gateway_id()

        response = self._http(
            "zones/polling", send_token=True,
            data={"gateWayId": gateway_id}
        )

        home = response.json()

        status = home.get('status', 1)
        if status != 0:
            raise RuntimeError(
                "Error getting zones from home: {}".format(status))

        if "data" not in home:
            raise RuntimeError(
                "Error getting zones from home: no data found")
        if "timestamp" not in home:
            raise RuntimeError(
                "Error getting zones from home: no timestamp found")

        for zone in home["data"]:
            zone["timestamp"] = home["timestamp"]

        return home["data"]

    def get_zones(self):
        """
        Get all zones
        """
        home_data = self.get_home()
        if not home_data:
            return []

        return home_data

    def get_zone_names(self):
        """
        Get the name of all zones
        """
        zone_names = []
        for zone in self.get_zones():
            zone_names.append(zone['name'])

        return zone_names

    def get_zone(self, name):
        """
        Get the information about a particular zone
        """
        for zone in self.get_zones():
            if name == zone['name']:
                return zone

        raise RuntimeError("Unknown zone: %s" % name)

    def is_zone_active(self, name):
        """
        Check if a zone is active
        """
        zone = self.get_zone(name)
        return zone_is_active(zone)

    def is_zone_boiler_on(self, name):
        """
        Check if the named zone's boiler is on and burning fuel (experimental)
        """
        zone = self.get_zone(name)
        return boiler_state(zone) == 2

    def get_zone_temperature(self, name):
        """
        Get the temperature for a zone
        """
        zone = self.get_zone(name)
        return zone_current_temperature(zone)

    def get_zone_target_temperature(self, name):
        """
        Get the temperature for a zone
        """
        zone = self.get_zone(name)
        return zone.get('targettemperature', -1)

    def get_zone_boost_temperature(self, name):
        """
        Get the boost target temperature for a zone
        """
        zone = self.get_zone(name)
        return zone_boost_temperature(zone)

    def is_boost_active(self, name):
        """
        Check if boost is active for a zone
        """
        zone = self.get_zone(name)
        return zone.get('isboostactive', False)

    def boost_hours(self, name):
        """
        Get the boost duration for a zone, in hours
        """
        zone = self.get_zone(name)
        return zone_boost_hours(zone)

    def boost_timestamp(self, name):
        """
        Get the timestamp recorded for the boost
        """
        zone = self.get_zone(name)
        return datetime.datetime.fromtimestamp(zone_boost_timestamp(zone))

    def is_target_temperature_reached(self, name):
        """
        Check if a zone temperature has reached the target temperature
        """
        zone = self.get_zone(name)
        return is_target_temperature_reached(zone)

    def set_zone_target_temperature(self, name, target_temperature):
        """
        Set the target temperature for a named zone
        """
        zone = self.get_zone(name)
        return self._set_zone_target_temperature(
            zone, target_temperature
        )

    def set_zone_advance(self, name, advance_state=True):
        """
        Set the advance state for a named zone
        :param bool advance_state: True to set advance, or False to cancel
        """
        zone = self.get_zone(name)
        return self._set_zone_advance(
            zone, advance_state
        )

    def activate_zone_boost(self, name, boost_temperature=None,
                            num_hours=1):
        """
        Turn on boost for a named zone
        """
        return self._set_zone_boost(
            self.get_zone(name), boost_temperature,
            num_hours
        )

    def deactivate_zone_boost(self, name):
        """
        Turn off boost for a named zone
        """
        zone = self.get_zone(name)
        return self._cancel_zone_boost(zone)

    def set_zone_mode(self, name, mode):
        """
        Set the mode by using the name of the zone
        Supported zones are available in the enum ZoneMode
        """
        if isinstance(mode, int):
            mode = ZoneMode(mode)

        assert isinstance(mode, ZoneMode)

        return self._set_zone_mode(
            self.get_zone(name), mode.value
        )

    def get_zone_mode(self, name):
        """
        Get the mode for a zone
        """
        zone = self.get_zone(name)
        return zone_mode(zone)

    def reset_login(self):
        """
        reset the login data to force a re-login
        """
        self._login_data = None

    # Ctor
    def __init__(self, username, password, cache_home=False):
        """Performs login and save session cookie."""

        if cache_home:
            raise RuntimeError("cache_home not implemented")

        self._login_data = None
        self._user = {
            'user_id': None,
            'username': username,
            'password': password
        }

        # This is the list of homes / gateways associated with the account.
        self._homes = None

        self._home_details = None

        self._refresh_token_validity_seconds = 1800

        self.http_api_base = 'https://eu-https.topband-cloud.com/ember-back/'

        if not self._login():
            raise RuntimeError("Unable to login.")
