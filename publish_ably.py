##############################################
#### Written By: SATYAKI DE               ####
#### Written On: 20-Dec-2020              ####
#### Modified On 20-Dec-2020              ####
####                                      ####
#### Objective: Calling Twilio Voice API  ####
##############################################

from ably import AblyRest
import logging
import json

# generate random floating point values
from random import seed
from random import random
# seed random number generator
seed(1)

logger = logging.getLogger('ably')
logger.addHandler(logging.StreamHandler())

ably = AblyRest('XXXXX.RRRR822:0293jfkdkdkeflE')
channel = ably.channels.get('sd_channel')

# JSON data
json_data = [{
    "Currency": "INR",
    "CurrentExchange": 71.23,
    "Change": 9.23
},{
    "Currency": "GBR",
    "CurrentExchange": 0.123,
    "Change": -0.01
},{
    "Currency": "EUR",
    "CurrentExchange": 0.83,
    "Change": 3.49
},
    {
    "Currency": "YEN",
    "CurrentExchange": 123.09,
    "Change": 2.75
    }]

jdata = json.dumps(json_data)

# Publish a message to the sd_channel channel
channel.publish('event', jdata)

# Adding Multiple values
for i in range(30):
    json_data_2 = [
        {
            "Currency": "INR",
            "CurrentExchange": round((7.123 * random() * 100), 2),
            "Change": round((0.014 * random() * 100), 2)
        },
        {
            "Currency": "GBR",
            "CurrentExchange": round((0.123 * random() * 100), 2),
            "Change": -1 * round((0.054 * random() * 100), 2)
        },
        {
            "Currency": "EUR",
            "CurrentExchange": round((8.23 * random() * 100), 2),
            "Change": -1 * round((0.004 * random() * 100), 2)
        },
        {
            "Currency": "YEN",
            "CurrentExchange": round((0.124 * random() * 100), 2),
            "Change": round((0.076 * random() * 100), 2)
        }
    ]

    jdata_2 = json.dumps(json_data_2)

    # Publish a message to the sd_channel channel
    channel.publish('event', jdata_2)

    json_data_2 = []
    jdata_2 = ''

