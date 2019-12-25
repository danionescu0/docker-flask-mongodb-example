import json
import time, datetime
import statistics
import requests

import paho.mqtt.client as mqtt
from pymongo import MongoClient


influxdb_url = 'http://influxdb:8086/write?db=influx'
sensors = MongoClient('mongo', 27017).demo.sensors
client = mqtt.Client()
client.username_pw_set('some_user', 'some_pass')


# on connect to MQTT server subscribes to all topics
def on_connect(client, userdata, flags, rc):
    client.subscribe('sensors')


def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode("utf-8")
        decoded_data = json.loads(message)
    except Exception as e:
        print('could not decode message {0}'.format(message))
        print(str(e))
        return

    # skip processing if it's averages topic to avoid an infinit loop
    sensors.update_one(
        {"_id": decoded_data['sensor_id']},
        {"$push": {
            "items": {
                "$each": [{"value": decoded_data['sensor_value'], "date": datetime.datetime.utcnow()}],
                "$sort": {"date": -1},
                "$slice": 5
            }
        }},
        upsert=True
    )
    #add data to grafana through influxdb
    try:
        requests.post(url=influxdb_url, data='{0} value={1}'.format(
            decoded_data['sensor_id'], decoded_data['sensor_value']))
    except Exception as e:
        print(str(e))
    # obtain the mongo sensor data by id
    sensor_data = list(sensors.find({"_id" : decoded_data['sensor_id']}))
    # we extract the sensor last values from sensor_data
    sensor_values = [d['value'] for d in sensor_data[0]['items']]
    client.publish('averages/{0}'.format(decoded_data['sensor_id']), statistics.mean(sensor_values), 2)


client.on_connect = on_connect
client.on_message = on_message

client.connect('mqtt', 1883, 60)
client.loop_start()

while True:
    time.sleep(0.05)