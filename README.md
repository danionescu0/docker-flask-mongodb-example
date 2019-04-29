## Purpose

**A working demo usage of docker, docker-compose, mongodb, python3, docker-compose, mosquitto, swagger to serve as a demo**

**If you consider this demo usefull give it a star so other will find it quicker :)**

The applications will run in parallel using docker-compose on different ports:

**1** [Random service](#random-service) generates random numbers and lists them (port 80)

**2** [CRUD service](#CRUD-service) Create, read, update and detele operations over a user collection (port 81)

**3** [MQTT service](#MQTT-service) will use a MQTT server (Mosquitto) to allow to publish sensor updates over MQTT  (port 1883)
The updates will be saved in mongodb (/demo/sensors). It will also compute a running average 
for each sensor and publish it to a separate topic

**4** [Fulltext service](#Fulltext-service) fulltext search engine backed by fulltext mongoDb index (port 82)

**5** [Geospacial search service](#Geospacial-search-service) geospacial search service that supports adding places, and quering the placing by coordonates and distance (port 83)



![diagram.png](https://github.com/danionescu0/docker-flask-mongodb-example/blob/master/resources/diagram.jpg)


## Technollogies involved
* [Docker](https://opensource.com/resources/what-docker) A container system

How to install docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04

How to install docker compose: https://docs.docker.com/compose/install/

* [docker-compose](https://docs.docker.com/compose/) Docker containers orchestraion system

* [python](https://www.python.org/doc/essays/blurb/) Programming language

* [MongoDb] (https://www.mongodb.com/) General purpose NoSQL database system

* [flask microframework](http://flask.pocoo.org/) Python web framework 

* [Mosquitto MQTT] (https://mosquitto.org/) MQTT server

* [Curl] (https://curl.haxx.se/) Linux tool for performing HTTP requests

* [Swagger](https://swagger.io/) A tool for documention HTTP requests for using OpenAPI specification: https://github.com/OAI/OpenAPI-Specification

* [Locust.io](https://locust.io/) A open source load testing tool. Here is used as a stress test tool



## Run the microservice
Before running check that the ports are available and free on your machine!

````
docker-compose up
````

## Testing the architecture

**Manual testing:**

For all HTTP requests we'll be using [curl][https://curl.haxx.se/docs/manpage.html]
An alternative manual HTTP testing you could use Swagger, for example for crud operations in a browser open: 
http://localhost:81/apidocs to see the Swagger UI and to perform test requests from there!

For the MQTT application we'll use mosquitto cli
In most UNIX systems curl is already installed, to install mosquitto cli use:
````
sudo apt-get install mosquitto-clients
````

To load the test data i provided, you can use mongorestore after starting the services like this:
````
cd docker-flask-mongodb-example
docker compose up
mongorestore -d demo ./resources/demo-data/
````

**Stresstesting using locusts tool**

Using locust.io

Installation: https://docs.locust.io/en/stable/installation.html
Quickstart: https://docs.locust.io/en/stable/quickstart.html

Testing random demo microservice:
````
locust -f random-demo.py --host=http://localhost:80
````
Testing crud microservice:
````
locust -f crud.py --host=http://localhost:81
````

Testing fulltext_search microservice:
````
locust -f fulltext_search.py --host=http://localhost:82
````

Testing geolocation_search microservice:
````
locust -f geolocation_search.py --host=http://localhost:83
````

After starting any service open http://localhost:8089 to acces the testing UI

# Random service

This service generates random numbers and store them in a capped array (last 5 of them). Also it can generate
and return a random number.
 
The random number collection has only one documents with '_id' lasts and an "items" key that will be a capped array.

MongoDb official documentation (array operations): https://docs.mongodb.com/manual/reference/operator/update/slice/

* Generate a random number between 10 and 100 and returns it:
````
curl -i "http://localhost/random?lower=10&upper=100"
````

* Generate a random number between 10 and 100 and saves it into the capped array: 
````
curl -X PUT -i "http://localhost/random" -d lower=10 -d upper=20
````

* View last 5 generated numbers list: 

````
curl -i "http://localhost/random-list"
````

# CRUD service

CRUD stands for create, read, update, delete operations. I've written a demo for these operations on a collections
of users. A user has a userid, name and email fields.


* PUT request, this request will add a user with a userid, name and email:

example: add a new user with name dan email test@yahoo.com and userid 189
````
curl -X PUT -d email=test@yahoo.com -d name=dan http://localhost:81/users/189
````

* POST request, this request will modify a user name or email or both:

example, modify the email of the user with id 10

````
curl -X POST -d email=test22@yahoo.com  http://localhost:81/users/10

````

* GET request, this request will output as json the id, name and email of the user

example for with id 1:
````
curl -i "http://localhost:81/users/1"
````

* DELETE request, this request will delete a user with a specified id

example for with id 1:
````
curl -X DELETE -i "http://localhost:81/users/1"
````

# MQTT service

This usecase uses MQTT protocol instead of HTTP to communicate. It involves storing last 5 numerical values of a sensor,
running a moving average on them and publishing the average each time on a different topic.

* To update a sensor with id: "some_sensor" and value "some_value" use:

````
mosquitto_pub -h localhost  -p 1883  -d -t some_sensor -m some_value
````
This will publish to mosquitto in a topic named "some_sensor" and value "some_value".

Our python script will listen to this topic too, and save in the mongo sensors collections
the value for the sensor in a capped array.

After it writes the new values, it reads the last 5 values and computes an average (running average)
and publish it to topic "average/some_sensor"

* To get updates for sensor "some_sensor" use:
````
mosquitto_sub -h localhost  -p 1883 -d -t some_sensor
````
This will just listen for updates for the topic "some_sensor"

* To get updates for the average 5 values for sensor "some_sensor" use:
````
mosquitto_sub -h localhost  -p 1883 -d -t averages/some_sensor
````

This will just listen for updates for the topic "averages/some_sensor" and get a running average 
for the sensor "some_sensor". Each time someone publishes a new value for a sensor, the 
python script will calculate the average values of last 5 values and publishes it


# Fulltext service

This service exposes a REST API for inserting a text into the full text database, and retriving last 10 matches
MongoDb official documentation (text search): https://docs.mongodb.com/manual/text-search/
* To index a new expression like "ana has many more apples":
````
curl -X PUT -d expression="ana has many more apples"  http://localhost:82/fulltext
````

* To get all indexed expressions containing word "who"
````
curl -i "http://localhost:82/search/who"
````

# Geospacial search service

The service will allow to insert locations with coordonats (latitude and longitude), and will expose an REST API
to all locations near a point.

MongoDb official documentation(geospacial index): https://docs.mongodb.com/manual/geospatial-queries/

* To add a location named "Bucharest" with latitude 26.1496616 and longitude 44.4205455
````
curl -X POST -d name=Bucharest -d lat="26.1496616" -d lng="44.4205455"  http://localhost:5000/location
````

* To get all locations near 26.1 latitude and 44.4 longitude in a range of 5000 meeters (5 km)
````
curl -i "http://localhost:83/location/26.1/44.4?max_distance=50000"
````
