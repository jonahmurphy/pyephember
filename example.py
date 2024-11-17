"""
Example script for PyEphEmber to dump various information from the API,
get the current temperature, and change the target temperature for a zone
"""
import argparse
import getpass
import json
import time

from pyephember.pyephember import (
    EphEmber,
    zone_is_target_temperature_reached, 
    zone_is_target_boost_temperature_reached,
    zone_advance_active,
    zone_is_boost_active,
    zone_is_scheduled_on,
    zone_boost_hours,
    zone_boost_temperature,
    zone_current_temperature,
    zone_is_active,
    zone_is_hot_water,
    zone_mode,
    zone_name,
    zone_target_temperature,
)

# global params
parser = argparse.ArgumentParser(prog='example',
                                 description='Example of using pyephember')
parser.add_argument("--email", type=str, required=True,
                    help="Email Address for your account")
parser.add_argument('--password', type=str, default="",
                    help="Password for your account")
parser.add_argument('--zone-name', type=str, default="heating",
                    help="Zone name to check")
parser.add_argument(
    '--cache-home', type=bool, default=False,
    help="cache data between API requests"
)
parser.add_argument('--target', type=float,
                    help="Set new target temperature for the named Zone")
parser.add_argument('--advance', type=str, choices=("on","off"),
                    help="Set advance state for named Zone")
parser.add_argument('--boost', type=str, choices=("on","off"),
                    help="Set boost state for named Zone. Target boost temp hardcoded to current temp + 1 degree, and boost hours to 1hr")
args = parser.parse_args()

password = args.password
if not password:
    password = getpass.getpass()

t = EphEmber(args.email, password, cache_home=args.cache_home)

# Get the full home information
print(json.dumps(t.get_home(), indent=4, sort_keys=True))
print("----------------------------------")
# Get only zone information
print(json.dumps(t.get_zones(), indent=4, sort_keys=True))
print("----------------------------------")
# Get a zone by name
zone = t.get_zone(args.zone_name)
print(json.dumps(zone, indent=4, sort_keys=True))
print("----------------------------------")

# Get information about a zone
print("{} current temperature is {}".format(
    zone_name(zone), zone_current_temperature(zone)))
print("{} target temperature is {}. Is Reached: {}".format(
    args.zone_name, zone_target_temperature(zone), zone_is_target_temperature_reached(zone)))

print("{} active : {}".format(
    args.zone_name, zone_is_active(zone)
))
print("{} mode : {}".format(
    args.zone_name, zone_mode(zone)
))
print("{} advance active : {}".format(
    args.zone_name, zone_advance_active(zone)
))

print("{} is schedule on?: {}".format(
    args.zone_name, zone_is_scheduled_on(zone)
))

print("{} is hot water thermostat?: {}".format(
    args.zone_name, zone_is_hot_water(zone)
))

print("{} is boost active? : {}".format(
    args.zone_name, zone_is_boost_active(zone)
))

if zone_is_boost_active(zone):
    print("{} Boost Hours: {}, target temperature: {}, boost temperature: {}, reached? {}".format(
        args.zone_name, 
        zone_boost_hours(zone), 
        zone_target_temperature(zone),  
        zone_boost_temperature(zone),
        zone_is_target_boost_temperature_reached(zone)
    ))
    

target = args.target
if target is not None:
    assert 0 <= target <= 25.5
    t.set_zone_target_temperature(args.zone_name, target)
    time.sleep(1)
    print("{} target temperature changed to {}".format(
        args.zone_name, t.get_zone_target_temperature(args.zone_name)
    ))

if args.advance is not None:
    print("Setting advance for {} to {}".format(args.zone_name, args.advance))
    if args.advance == 'on':
        t.set_zone_advance(args.zone_name, True)
    elif args.advance == 'off':
        t.set_zone_advance(args.zone_name, False)
        
if args.boost is not None:
    if args.boost == 'on':
        print("Activating boost for {}, defaulting to +1 degree and 1hr".format(args.zone_name))
        target_temp = zone_current_temperature(zone) + 1
        t.activate_zone_boost(args.zone_name, boost_temperature=target_temp)
    elif args.boost == 'off':
        print("Deactivating boost for {}".format(args.zone_name))
        t.deactivate_zone_boost(args.zone_name)