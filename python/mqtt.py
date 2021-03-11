from logging import RootLogger
import json, time, datetime, statistics, requests

import paho.mqtt.client
from pymongo import MongoClient, errors

from utils import get_logger, read_docker_secret


influxdb_url = "http://influxdb:8086/write?db=influx"
mongo_host = "mongodb"
mqtt_host = "mqtt"
mqtt_user = read_docker_secret("MQTT_USER")
mqtt_password = read_docker_secret("MQTT_PASSWORD")

mongo_client = MongoClient(mongo_host, 27017)
sensors = mongo_client.demo.sensors
logger = get_logger()


class Mqtt:
    def __init__(self, host: str, user: str, password: str, logger: RootLogger) -> None:
        self.__host = host
        self.__user = user
        self.__password = password
        self.__logger = logger
        self.__topic = None

    def connect(self, topic: str):
        self.__topic = topic
        client = paho.mqtt.client.Client()
        client.username_pw_set(mqtt_user, mqtt_password)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(self.__host, 1883, 60)
        client.loop_start()

    def on_connect(
        self, client: paho.mqtt.client.Client, userdata, flags: dict, rc: int
    ):
        client.subscribe(self.__topic)

    def on_message(
        self,
        client: paho.mqtt.client.Client,
        userdata,
        msg: paho.mqtt.client.MQTTMessage,
    ):
        try:
            message = msg.payload.decode("utf-8")
            decoded_data = json.loads(message)
        except Exception as e:
            self.__logger.error(
                "could not decode message {0}, error: {1}".format(msg, str(e))
            )
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
            self.__logger.error(
                "Error writing to influxdb {0}, error: {1}".format(msg, str(e))
            )
        # obtain the mongo sensor data by id
        sensor_data = list(sensors.find({"_id": decoded_data["sensor_id"]}))
        # we extract the sensor last values from sensor_data
        sensor_values = [d["value"] for d in sensor_data[0]["items"]]
        client.publish(
            "averages/{0}".format(decoded_data["sensor_id"]),
            statistics.mean(sensor_values),
            2,
        )


mqtt = Mqtt(mqtt_host, mqtt_user, mqtt_password, logger)
mqtt.connect("sensors")

logger.debug("MQTT App started")
try:
    mongo_client.admin.command("replSetInitiate")
except errors.OperationFailure as e:
    logger.error("Error setting mongodb replSetInitiate error: {0}".format(str(e)))

while True:
    time.sleep(0.05)
