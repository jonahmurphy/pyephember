# API

Note: I have no connection with EPHControls and this API may be subject to change. Use of this API is at your own risk.

## API versions

The ember API was updated in January 2021, and again since then and users are slowly being moved to the new API. 
The documents describing the older API's from 2020-2023 are available from in [API Docs 2020](API_2020.md) and [API Docs 2021](API_2021.md)

## Intro

The ember API is a HTTPs based. 

HTTP with JSON is used for authentication, admin, and getting and updating some zone information (e.g. target temperature). 

## URLS

### HTTP

The base HTTP URL is https://eu-https.topband-cloud.com/ember-back. This will be referred to as $HTTP_ENDPOINT for the rest of the document. 


# HTTP API Calls

## Login

Initial login uses the email and password you used to register with the system. Subsequent requests are then authenticated using an access token that is returned during the initial login.

You can use any valid user for this but it would be a good idea to not use the super user for your home and have a dedicated API user

### Request

To login for the first time send a POST to $HTTP_ENDPOINT/appLogin/login with a JSON request containing your username and password.

```
POST /ember-back/appLogin/login HTTP/2.0
Accept	application/json
Content-Type	application/json;charset=utf-8
```

The form data to POST is

```
{
	"password": "password",
	"model": "iPhone XS",
	"os": "13.5",
	"type": 1,
	"appVersion": "2.4.2",
	"userName": "user@email.com"
}
```

### Response

The response is JSON in the format

```
{
	"data": {
		"refresh_token": "long_refresh_token",
		"token": "long_token"
	},
	"message": null,
	"status": 0,
	"timestamp": 1615150233365
}
```

The `token` is required for subsequent requests so it is important to keep this, this should be sent in the Authorization header for all other requests. 

The `refresh_token` can be used to update the authorization token and should be kept if you are planning on having longer sessions.

## Refresh Auth Token

To refresh your access token, send a GET to `$HTTP_ENDPOINT/appLogin/refreshAccessToken` using the `refresh_token` from your login request in the Authorization header 

It is unclear how long an access token last for however, it looks to last at least 1 hour. 

```
GET /ember-back/appLogin/refreshAccessToken HTTP/2.0
Accept	application/json
Authorization	long_refresh_token
```

### Response

The response contains the new authorization and refresh tokens.

```
{
	"data": {
		"refresh_token": "new_long_refresh_token",
		"token": "new_long_token"
	},
	"message": null,
	"status": 0,
	"timestamp": 1572718395062
}
```

## Report Token

The report token message is sent after login. It is unknown that this message does but I don't believe it is required for general usage of the API.

### Request

The request is a POST to `$HTTP_ENDPOING/user/reportToken` 

```
GET /ember-back/user/reportToken HTTP/2.0
Authorization	long_token
Accept	application/json
```

With the following JSON

```
{
	"os": "ios",
	"phoneToken": "really_long_phone_token",
	"type": 1,
	"appVersion": "2.0.4"
}
```

### Response

The response is the following JSON.

```
{
	"data": null,
	"message": null,
	"status": 0,
	"timestamp": 1615150233469
}
```


## Select User

After login the select user call is made to get user information for the app. 


To make a call to select user send a GET request to `$HTTP_ENDPOING/user/selectUser` with the token in the Authourization header. 

### Request

```
GET /ember-back/user/selectUser HTTP/2.0
Authorization	long_token
Accept	application/json
```

### Response

The response is a JSON message that includes information about the user.


```

{
	"data": {
		"accessfailedcount": 0,
		"appVersion": "2.0.4",
		"areacode": null,
		"email": "user@email.com",
		"emailconfirmed": true,
		"firstname": "Me",
		"id": 1111,
		"ip": null,
		"lastname": "Me",
		"lockoutenabled": true,
		"lockoutenddateutc": null,
		"model": "iPhone XS",
		"newsmarketing": false,
		"os": "13.5",
		"phonenumber": "0871234567",
		"phonenumberconfirmed": false,
		"primaryexternalloginprovider": null,
		"profilepictureuri": null,
		"profilepicurelastsynced": null,
		"protocolstatus": 1,
		"registrationtime": null,
		"securitystamp": "f9e3098b-7b99-45a0-bc23-7f4b399edde6",
		"synchroniseprofilepicture": false,
		"systemmaintenance": false,
		"twofactorenabled": false,
		"type": 2,
		"useprimaryexternalproviderpicture": false,
		"username": "user@email.com"
	},
	"message": "The query is successful",
	"status": 0,
	"timestamp": 1615150233473
}
```

## Get Available Homes

To get the list of available homes 

### Request

The request is a GET to the URL `$ENDPOINT/homes/list`.

```
GET /ember-back/homes/list HTTP/2.0
Authorization	long_token
Accept	application/json
Content-Length	0
```

### Response

The response is a JSON Blob describing the homes available to your account.

```
{
	"data": [{
        "deviceType": 1,
        "ecoSwitch": 0,
        "frostprotectionenabled": false,
        "gatewayid": "gwyid123",
        "groupSwitch": 0,
        "holidayStatus": 0,
        "holidaymodeactive": false,
        "invitecode": "XXXX",
        "name": "Home",
        "productId": "",
        "quickboosttemperature": 0,
        "sysTemType": "EMBER-PS",
        "uid": "",
        "weatherlocation": "",
        "zoneCount": 3
        "sysTemType": "EMBER-PS"
    }],
	"message": "succ.",
	"status": 0,
	"timestamp": 1615150233565
}
```

The `gatewayid` is required for later requests to identify the home that is being controlled.

## Note

Payload schema has changed a little since the 2021 update, but fortunately in a way which was backward compatible for this library. 

## Get Home Details

To get details of your home, you should use the `gatewayid` returned from the `homes/list` request above.

### Request

The request is a POST to the URL `$ENDPOINT/homes/detail` passing the `gatewayid` in a JSON request

```
GET /ember-back/homes/detail HTTP/2.0
Authorization	long_token
Accept	application/json
```

The JSON to send is:

```
{
	"gateWayId": "gwid1111"
}
```

### Response
Payload schema has changed a little since the 2021 update, but fortunately in a way which was backward compatible for this library. 
New example response is shown below.

The response is JSON:

```
{
	"data": {
        "curAccess": {
            "boost": true,
            "homemanagement": true,
            "homeuserid": "xxxxx",
            "operatedAction": 0,
            "roleId": 3,
            "schedulesmanagement": true
        },
        "homes": {
            "deviceType": 1,
            "ecoSwitch": 0,
            "frostprotectionenabled": false,
            "gatewayid": "gwid123",
            "groupSwitch": 0,
            "holidayStatus": 0,
            "holidaymodeactive": false,
            "invitecode": "1234",
            "name": "Home",
            "productId": "",
            "quickboosttemperature": 20,
            "sysTemType": "EMBER-PS",
            "uid": "",
            "weatherlocation": "",
            "zoneCount": 3
        },
        "mcuVersion": 0,
        "settings": {
            "newuserhasjoinedhome": true,
            "userid": "123456",
            "zonescheduleupdated": true
        },
        "wifiVersion": 0
    },
	"message": "succ.",
	"status": 0,
	"timestamp": 1615150236340
}
```

## Get Zones Information

To get details of your available zones, you should send the `gatewayid` to the `zones/polling` endpoint.

### Request
Older 2020 API, in use again? 


The request is a POST to the URL `$ENDPOINT/zones/polling` passing the `gatewayid` in a JSON request

> [!NOTE]
> This is a new API which replaces the older `homesVT/zoneProgram` API


```
GET /ember-back/zones/polling HTTP/2.0
Authorization	long_token
Accept	application/json
```

The JSON to send is:

```
{
	"gateWayId": "gwid1111"
}
```

### Response

The response is JSON 

JSON response is:

```
{
    "data": [
        {
            "areaid": null,
            "boostActivations": {
                "activatedon": "2024-10-14 12:58:40.650",
                "comments": null,
                "dispayFinishdatetime": "2024-10-14 14:58:40.650",
                "finishdatetime": "2024-10-14 13:58:40.650",
                "numberofhours": 1,
                "targettemperature": 48.0,
                "userid": 12345,
                "wascancelled": false,
                "zoneboostactivationid": 5468795,
                "zoneid": zid12
            },
            "boostTime1": null,
            "boostTime2": null,
            "boostTime3": null,
            "currenttemperature": 20.5,
            "hardwareid": "2",
            "homeName": null,
            "hour": 0,
            "isadvanceactive": false,
            "isboostactive": true,
            "ishotwater": true,
            "isonline": true,
            "mode": 0,
            "name": "Hot Water",
            "prefix": "This zone is off until 20:00",
            "programmes": {
                "friday": {
                    "dayperiodid": 661828,
                    "p1": {
                        "endtime": "09:00",
                        "periodid": 1985482,
                        "starttime": "09:00"
                    },
                    "p2": {
                        "endtime": "12:00",
                        "periodid": 1985483,
                        "starttime": "12:00"
                    },
                    "p3": {
                        "endtime": "20:00",
                        "periodid": 1985484,
                        "starttime": "20:00"
                    }
                },
                "fridayDayperiodid": 661828,
                "monday": {
                    "dayperiodid": 661824,
                    "p1": {
                        "endtime": "09:00",
                        "periodid": 1985470,
                        "starttime": "09:00"
                    },
                    "p2": {
                        "endtime": "12:00",
                        "periodid": 1985471,
                        "starttime": "12:00"
                    },
                    "p3": {
                        "endtime": "20:00",
                        "periodid": 1985472,
                        "starttime": "20:00"
                    }
                },
                "mondayDayperiodid": 661824,
                "saturday": {
                    "dayperiodid": 661829,
                    "p1": {
                        "endtime": "09:00",
                        "periodid": 1985485,
                        "starttime": "09:00"
                    },
                    "p2": {
                        "endtime": "12:00",
                        "periodid": 1985486,
                        "starttime": "12:00"
                    },
                    "p3": {
                        "endtime": "20:00",
                        "periodid": 1985487,
                        "starttime": "20:00"
                    }
                },
                "saturdayDayperiodid": 661829,
                "sunday": {
                    "dayperiodid": 661823,
                    "p1": {
                        "endtime": "09:00",
                        "periodid": 1985467,
                        "starttime": "09:00"
                    },
                    "p2": {
                        "endtime": "12:00",
                        "periodid": 1985468,
                        "starttime": "12:00"
                    },
                    "p3": {
                        "endtime": "20:00",
                        "periodid": 1985469,
                        "starttime": "20:00"
                    }
                },
                "sundayDayperiodid": 661823,
                "thursday": {
                    "dayperiodid": 661827,
                    "p1": {
                        "endtime": "09:00",
                        "periodid": 1985479,
                        "starttime": "09:00"
                    },
                    "p2": {
                        "endtime": "12:00",
                        "periodid": 1985480,
                        "starttime": "12:00"
                    },
                    "p3": {
                        "endtime": "20:00",
                        "periodid": 1985481,
                        "starttime": "20:00"
                    }
                },
                "thursdayDayperiodid": 661827,
                "tuesday": {
                    "dayperiodid": 661825,
                    "p1": {
                        "endtime": "09:00",
                        "periodid": 1985473,
                        "starttime": "09:00"
                    },
                    "p2": {
                        "endtime": "12:00",
                        "periodid": 1985474,
                        "starttime": "12:00"
                    },
                    "p3": {
                        "endtime": "20:00",
                        "periodid": 1985475,
                        "starttime": "20:00"
                    }
                },
                "tuesdayDayperiodid": 661825,
                "wednesday": {
                    "dayperiodid": 661826,
                    "p1": {
                        "endtime": "09:00",
                        "periodid": 1985476,
                        "starttime": "09:00"
                    },
                    "p2": {
                        "endtime": "12:00",
                        "periodid": 1985477,
                        "starttime": "12:00"
                    },
                    "p3": {
                        "endtime": "20:00",
                        "periodid": 1985478,
                        "starttime": "20:00"
                    }
                },
                "wednesdayDayperiodid": 661826,
                "zoneid": zid12
            },
            "receiverid": 12355,
            "scenarioScenarioid": null,
            "startTime": 1728910720,
            "status": 1,
            "storedtargettemperature": 47.0,
            "targettemperature": 47.0,
            "zoneid": zid12
        }
    ],
    "message": "succ.",
    "status": 0,
    "timestamp": 1731803378558
}
```

### Notes

This request is one of the brand new requests from the new API. It includes information from all zones including:

  * Timer schedule. 
  * Target temperature
  * Current temperature
  * Boost Activations information
  * etc

## Boost Zone
Older 2020 API, in use again? 


To activate boost for  given zone use the following API, with which
you can set the boost time (1-3 hrs) and target temperature.

### Request
```
POST /ember-back/zones/boost 
Authorization: long_token
```

The JSON to send is:

```
{"hours": 1.0,"temperature":21.0,"zoneid":"zid12"}
```

> [!NOTE]
> The response body is empty for this API.

## Cancel Boost

### Request

Older 2020 API, in use again? 

```
POST /ember-back/zones/cancelBoost
Authorization: long_token
```

The JSON to send is:

```
{"zoneid":"zid12"}
```

> [!NOTE]
> The response body is empty for this API.

## Set Zone Temperature

### Request

```
POST /ember-back/zones/setTargetTemperature
Authorization: long_token
```

The JSON to send is:

```
{"temperature":20.0,"zoneid":"zid12"}
```

> [!NOTE]
> The response body is empty for this API.

## Zone Advance

Older 2020 API, in use again? 


### Request
```
POST /ember-back/zones/adv
Authorization: long_token
```

{"zoneid":"zid12"}

> [!NOTE]
> The response body is empty for this API.


## Cancel Zone Advance

Older 2020 API, in use again? 


### Request


```
POST /ember-back/zones/cancelAdv
Authorization: long_token
```

{"zoneid":"zid12"}

> [!NOTE]
> The response body is empty for this API.

## Set Mode
Older 2020 API, in use again? 


Use this API to change the mode.

> [!NOTE]
> Note the typos `model` vs `mode`, 
>  its likely they may fix those, and break the API.

Mode: 0=auto, 1=all day, 2=on, 3=off

### Request

```
POST /ember-back/zones/setModel
Authorization: long_token
```

{"zoneid":"zid12","model":1}