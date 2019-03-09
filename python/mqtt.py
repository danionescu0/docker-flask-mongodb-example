import time, datetime
import statistics

import paho.mqtt.client as mqtt
from pymongo import MongoClient


time.sleep(5) # hack for the mongoDb database and mqtt to get running
sensors = MongoClient('mongo', 27017).demo.sensors
client = mqtt.Client()


# on connect to MQTT server subscribes to all topics
def on_connect(client, userdata, flags, rc):
    client.subscribe('#')


def on_message(client, userdata, msg):
    sensor_value = float(msg.payload.decode("utf-8"))
    sensor_id = msg.topic
    # skip processing if it's averages topic to avoid an infinit loop
    if sensor_id.find('averages/') != -1:
        return
    sensors.update(
        {"_id": sensor_id},
        {"$push": {
            "items": {
                "$each": [{"value" : sensor_value, "date": datetime.datetime.utcnow()}],
                "$sort": {"date" : -1},
                "$slice": 5
            }
        }},
        upsert = True
    )
    # obtain the mongo sensor data by id
    sensor_data = list(sensors.find({"_id" : sensor_id}))
    # we extract the sensor last values from sensor_data
    sensor_values = [d['value'] for d in sensor_data[0]['items']]
    client.publish('averages/{0}'.format(sensor_id), statistics.mean(sensor_values), 2)


client.on_connect = on_connect
client.on_message = on_message
client.connect('mqtt', 1883, 60)
client.loop_start()

while True:
    time.sleep(0.05)