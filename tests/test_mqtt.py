import json
import requests
import pytest
import time
import os
from typing import Generator, Any

import paho.mqtt.client as mqtt

from utils import Collection


influx_query_url = "http://influxdb:8086/query?db=influx&"
# status for mqtt
SUCCESS = 0


@pytest.fixture
def sensors(demo_db) -> Generator[Collection, None, None]:
    collection = Collection(demo_db, "sensors")
    yield collection
    collection.drop()


@pytest.fixture
def mqtt_client() -> Generator[mqtt.Client, None, None]:
    username = ""
    password = ""
    parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secrets_path = os.path.join(parent_path, "secrets")

    with open(os.path.join(secrets_path, "mqtt_user.txt"), "r") as file:
        username = file.read()
    with open(os.path.join(secrets_path, "mqtt_pass.txt"), "r") as file:
        password = file.read()

    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(username, password)
    mqtt_client.connect("mqtt", 1883)
    yield mqtt_client
    mqtt_client.disconnect()


@pytest.mark.skip(reason="fix this test under gitlab ci")
def test_db_insert(mqtt_client, sensors):
    # publish message
    measurement = "temperature"
    cleanup_influx(measurement)
    mqtt_response = publish_message(
        mqtt_client,
        "sensors",
        json.dumps({"sensor_id": measurement, "sensor_value": 10}),
    )
    assert mqtt_response == SUCCESS

    # influx
    query = "q=SELECT * FROM {}".format(measurement)
    response = requests.get(influx_query_url + query)
    results = response.json()["results"]
    series = results[0]["series"]
    values = series[0]["values"]
    name = series[0]["name"]

    assert len(results) == 1
    assert name == measurement
    assert values[0][1] == 10
    mqtt_client.disconnect()

    # mongo
    response = sensors.get({})
    items = response[0]["items"]
    assert len(items) == 1
    assert items[0]["value"] == 10

    # delete data
    cleanup_influx(measurement)


def test_mqtt_publish(mqtt_client, sensors):
    measurement = "temperature"
    cleanup_influx(measurement)

    publish_message(
        mqtt_client,
        "sensors",
        json.dumps({"sensor_id": measurement, "sensor_value": 10}),
    )

    mqtt_client.subscribe("averages/{}".format(measurement))
    mqtt_client.on_message = check_message
    mqtt_client.loop_start()
    cleanup_influx(measurement)
    sensors.delete(measurement)


def publish_message(mqtt_client, topic: str, data: str) -> int:
    mqtt_response = mqtt_client.publish(topic, data)
    time.sleep(0.5)
    return mqtt_response[0]


# fix this on gitlab ci
def cleanup_influx(measurement: str) -> int:
    pass
    # resp = requests.post(
    #     'http://influxdb:8086/query?db=influx&q=DELETE FROM "{}"'.format(measurement)
    # )
    # return resp.status_code


def check_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
    message = msg.payload.decode("utf-8")
    decoded_data = json.loads(message)
    assert decoded_data["sensor_value"] == 10
