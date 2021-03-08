import json, time, datetime, statistics, requests

import paho.mqtt.client as mqtt
from pymongo import MongoClient, errors

from utils import get_logger, read_docker_secret


influxdb_url = "http://influxdb:8086/write?db=influx"
mongo_host = "mongodb"
mqtt_host = "mqtt"

mqtt_user = read_docker_secret("MQTT_USER")
mqtt_password = read_docker_secret("MQTT_PASSWORD")
print(mqtt_user, mqtt_password)

mongo_client = MongoClient(mongo_host, 27017)
sensors = mongo_client.demo.sensors
client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_password)
logger = get_logger()


# on connect to MQTT server subscribes to all topics
def on_connect(client, userdata, flags, rc):
    client.subscribe("sensors")


def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode("utf-8")
        decoded_data = json.loads(message)
    except Exception as e:
        logger.error("could not decode message {0}, error: {1}".format(msg, str(e)))
        logger.error("could not decode message {0}".format(message))
        return

    # skip processing if it's averages topic to avoid an infinit loop
    sensors.update_one(
        {"_id": decoded_data["sensor_id"]},
        {
            "$push": {
                "items": {
                    "$each": [
                        {
                            "value": decoded_data["sensor_value"],
                            "date": datetime.datetime.utcnow(),
                        }
                    ],
                    "$sort": {"date": -1},
                    "$slice": 5,
                }
            }
        },
        upsert=True,
    )
    # add data to grafana through influxdb
    try:
        requests.post(
            url=influxdb_url,
            data="{0} value={1}".format(
                decoded_data["sensor_id"], decoded_data["sensor_value"]
            ),
        )
    except Exception as e:
        logger.error("Erro writing to grafana {0}, error: {1}".format(msg, str(e)))
    # obtain the mongo sensor data by id
    sensor_data = list(sensors.find({"_id": decoded_data["sensor_id"]}))
    # we extract the sensor last values from sensor_data
    sensor_values = [d["value"] for d in sensor_data[0]["items"]]
    client.publish(
        "averages/{0}".format(decoded_data["sensor_id"]),
        statistics.mean(sensor_values),
        2,
    )


client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_host, 1883, 60)
client.loop_start()

logger.debug("MQTT App started")
try:
    mongo_client.admin.command("replSetInitiate")
except errors.OperationFailure as e:
    logger.error("Error setting mongodb replSetInitiate error: {0}".format(str(e)))

while True:
    time.sleep(0.05)
