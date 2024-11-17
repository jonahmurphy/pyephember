
POST /ember-back/zones/polling
{"gateWayId":"zzzzzz"}

response:
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


## Boost Zone

### Request
```
POST /ember-back/zones/boost 
Authorization: long_token
```

The JSON to send is:

```
{"hours": 1.0,"temperature":21.0,"zoneid":"zid12"}
```

### Cancel Boost

```
POST /ember-back/zones/cancelBoost
Authorization: long_token
```

The JSON to send is:

```
{"zoneid":"zid12"}
```


## Set Zone Temperature

```
POST /ember-back/zones/setTargetTemperature
Authorization: long_token
```

The JSON to send is:

```
{"temperature":20.0,"zoneid":"zid12"}
```

## Zone Advance

```
POST /ember-back/zones/adv
Authorization: long_token
```

{"zoneid":"zid12"}


## Cancel Zone Advance

```
POST /ember-back/zones/cancelAdv
Authorization: long_token
```

{"zoneid":"zid12"}


## Set Mode

```
POST /ember-back/zones/setModel
Authorization: long_token
```

{"zoneid":"zid12","model":1}