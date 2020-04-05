## Purpose

**A working demo usage of multiple technologies like: Docker, Docker-compose, MongoDb, Python3, Mosquitto, Swagger, Locusts, Grafana, InfluxDB**

**Please consider adding issues of bugs and enhancements**

**If you consider this demo usefull give it a star so others will find it quicker :)**


The applications will run using docker-compose::

**1** [Random service](#random-service) generates random numbers and lists them (port 800)

**2** [User CRUD service](#User-CRUD-service) Create, read, update and detele operations over a user collection (port 81)

**3** [MQTT service](#MQTT-service) will use a MQTT server (Mosquitto) to allow to publish sensor updates over MQTT  (port 1883)
The updates will be saved in mongodb (/demo/sensors). It will also compute a running average 
for each sensor and publish it to a separate topic

**4** [Fulltext service](#Fulltext-service) fulltext search engine backed by fulltext mongoDb index (port 82)

**5** [Geospacial search service](#Geospacial-search-service) geospacial search service that supports adding places, and quering the placing by coordonates and distance (port 83)

**6** [Baesian_average](#Baesian-average) baesian average demo (https://en.wikipedia.org/wiki/Bayesian_average) (port 84)

**7** [Photo process](#Photo-process) This is a demo of disk manipulation using docker volumes. 
Photos will be stored on disk retrived and resized / rotated. Also a search by image API will be available (port 85)

**8** [Book collection](#Book-collection) A virtual book library, has api methods for managing books, and borrowing book mechanisms.
The users must have "profiles" created using the User CRUD service. This api used flask rest plus (https://flask-restplus.readthedocs.io/en/stable/) 
(port 86)

**9** [Grafana and InfluxDb](#Grafana-and-InfluxDb) Grafana with InfluxDb storage. For showing graphs on sensors. 
It is connected with the MQTT service. Every datapoint that passes through the MQTT service will be saved in InfluxDb and displayed in Grafana.
(port 3000)


![Diagram](https://github.com/danionescu0/docker-flask-mongodb-example/blob/master/resources/diagram.jpg)
![Grafana](https://github.com/danionescu0/docker-flask-mongodb-example/blob/master/resources/grafana.png)

## Technollogies involved
* [Docker](https://opensource.com/resources/what-docker) A container system

How to install docker on Ubuntu: https://docs.docker.com/install/linux/docker-ce/ubuntu/

* [docker-compose](https://docs.docker.com/compose/) Docker containers orchestraion system

How to install docker compose: https://docs.docker.com/compose/install/

* [python](https://www.python.org/doc/essays/blurb/) Programming language

* [MongoDb](https://www.mongodb.com/) General purpose NoSQL database system

* [flask microframework](http://flask.pocoo.org/) Python web framework 

* [Mosquitto MQTT](https://mosquitto.org/) MQTT server

* [Curl](https://curl.haxx.se/) Linux tool for performing HTTP requests

* [Swagger](https://swagger.io/) A tool for documention HTTP requests for using OpenAPI specification: https://github.com/OAI/OpenAPI-Specification

* [Locust.io](https://locust.io/) A open source load testing tool. Here is used as a stress test tool

* [Grafana](https://grafana.com/) Grafana is the open source analytics & monitoring solution for every database

* [InfluxDb](https://www.influxdata.com/) Timeseries database, here used a storage to Grafana



## Run the microservice
Before running check that the ports are available and free on your machine!

On linux run the following command and check the output, if the ports 80 to 85, 1883 and 27017 are not available please change the ports accordingly in docker-compose.yaml 
````
netstat -nltp
````

Start the microservice architecture:
````
cd git_clonned_project_folder
docker-compose build
docker-compose up
````
Note: The build step is necessary only when modifying the source code (git pull or manually edit sources)

## Testing the architecture

**Manual testing:**

For all HTTP requests we'll be using [curl][https://curl.haxx.se/docs/manpage.html]. In most UNIX systems curl is already installed.
If you're using Debian/Ubuntu and you don't have curl try using:

````
sudo apt-get install curl
````

An alternative manual HTTP testing you could use Swagger, for example for users crud operations in a browser open: 
http://localhost:81/apidocs to see the Swagger UI and to perform test requests from there!

For the MQTT application we'll use mosquitto cli: To install mosquitto cli in Debian / Ubuntu use:
````
sudo apt-get install mosquitto-clients
````

To load the test data i provided in MongoDb, you can use mongorestore after starting the services like this:
````
cd docker-flask-mongodb-example
docker compose up
mongorestore -d demo ./resources/demo-data/
````

**Stress testing using locusts.io**

Using locust.io

Installation: https://docs.locust.io/en/stable/installation.html

Quickstart: https://docs.locust.io/en/stable/quickstart.html

Testing random demo microservice:
````
locust -f random-demo.py --host=http://localhost:800
````
Testing users microservice:
````
locust -f users.py --host=http://localhost:81
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


**API gateway using Krakend**
Website: https://www.krakend.io

Web configurator: https://designer.krakend.io/

The API gateway is installed inside this project using a docker container in docker.compose.yml, it loads it's 
configuration from krakend.json 

For demo purposes i've configured the gateway for two endpoints. The Krakend runs on port 8080

1. the random generator service (web-random), GET request
````
curl -i "http://localhost:8080/random?upper=10&lower=5"
````

2. the users service, (web-users), GET all users request
````
curl -i "http://localhost:8080/users?limit=5&offset=0"
````

All requests can be configured through this gateway using the json file or the web configurator.


# Random service

This service generates random numbers and store them in a capped array (last 5 of them). Also it can generate
and return a random number.
 
The random number collection has only one documents with '_id' lasts and an "items" key that will be a capped array.

MongoDb capped array: https://www.mongodb.com/blog/post/push-to-sorted-array

Sample data in "random_numbers" collection document:
````
{
  "_id" : "lasts",
  "items": [3, 9, 2, 1, 2]
}
...
````

MongoDb official documentation (array operations): https://docs.mongodb.com/manual/reference/operator/update/slice/

Swagger url: http://localhost:800/apidocs  

Api methods using Curl:

* Generate a random number between 10 and 100 and returns it:
````
curl -i "http://localhost:800/random?lower=10&upper=100"
````

* Generate a random number between 10 and 100 and saves it into the capped array: 
````
curl -X PUT -i "http://localhost:800/random" -d lower=10 -d upper=20
````

* View last 5 generated numbers list: 

````
curl -i "http://localhost:800/random-list"
````

# User CRUD service

CRUD stands for Create, Read, Update and Delete operations. I've written a demo for these operations on a collections
of users. A user has a userid, name and email fields.

Sample data in user collection document:
````
{
  "_id" : 12,
  "email": "some@gmail.com",
  "name": "some name"
}
...
````

Swagger url: http://localhost:81/apidocs

Api methods using Curl:

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

MQTT official link: http://mqtt.org/

MQTT explained: https://randomnerdtutorials.com/what-is-mqtt-and-how-it-works/

MQTT info, tools stuff: https://github.com/hobbyquaker/awesome-mqtt#tools

MongoDb capped array: https://www.mongodb.com/blog/post/push-to-sorted-array

Sample data in sensors collection document:
````
	"_id" : "some_sensor",
	"items" : [
		{
			"value" : 23,
			"date" : ISODate("2019-03-09T17:49:10.585Z")
		},
		{
			"value" : 5,
			"date" : ISODate("2019-03-09T17:49:08.766Z")
		},
        ... 3 more
	]
...
````

* To update a sensor with id: "some_sensor" and value "15.2" use:

````
mosquitto_pub -h localhost -u some_user -P some_pass -p 1883 -d -t sensors -m "{\"sensor_id\": \"temperature\", \"sensor_value\": 15.2}"
````
This will publish to mosquitto in the "sensors" topic the following json: {'sensor_id": 'temperature', 'sensor_value': 15.2}

Our python script will listen to this topic too, and save in the mongo sensors collections
the value for the sensor in a capped array.

After it writes the new values, it reads the last 5 values and computes an average (running average)
and publish it to topic "average/temperature"

* To get updates for all sensors use:
````
mosquitto_sub -h localhost -u some_user -P some_pass -p 1883 -d -t sensors
````
This will just listen for updates for the topic "sensors"

* To get updates for the average 5 values for sensor "temperature" use:
````
mosquitto_sub -h localhost -u some_user -P some_pass -p 1883 -d -t averages/temperature
````

This will just listen for updates for the topic "averages/temperature" and get a running average 
for the sensor "temperature". Each time someone publishes a new value for a sensor, the 
python script will calculate the average values of last 5 values and publishes it


# Fulltext service

This service exposes a REST API for inserting a text into the full text database, and retriving last 10 matches

MongoDb official documentation (text search): https://docs.mongodb.com/manual/text-search/

Sample data in fulltext_search collection document:
````
{
	"_id" : ObjectId("5c44c5104f2137000c9d8cb2"),
	"app_text" : "ana has many more apples",
	"indexed_date" : ISODate("2019-01-20T18:59:28.060Z")
}
...
````

Swagger url: http://localhost:82/apidocs

Api methods using Curl:

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

Sample data in places collection document:
````
{
	"_id" : ObjectId("5c83f901fc91f1000c29fb4d"),
	"location" : {
		"type" : "Point",
		"coordinates" : [
			-75.1652215,
			39.9525839
		]
	},
	"name" : "Philadelphia"
}
..
````

Swagger url: http://localhost:83/apidocs

Api methods using Curl:

* To add a location named "Bucharest" with latitude 26.1496616 and longitude 44.4205455
````
curl -X POST -d name=Bucharest -d lat="26.1496616" -d lng="44.4205455" http://localhost:84/location
````

* To get all locations near 26.1 latitude and 44.4 longitude in a range of 5000 meeters (5 km)
````
curl -i "http://localhost:84/location/26.1/44.4?max_distance=50000"
````

# Baesian average

This is a naive implementation of the baesian average (https://en.wikipedia.org/wiki/Bayesian_average).

It's naive because it's not built with scalability in mind. 

The baesian average is used in rating systems to add weight to the number of votes. 

In this example we'll use items and users. A user is represented by it's id and it rates items from 0 - 10

A Item it's represented by an id and a name and it's rated by the users.

A full rating example:

Items:
- id: 1, name: Hamlet, votes by users: 10
- id: 2, name: Cicero, votes by users: 9, 10, 9
- id: 3, name: Alfred, votes by users: 10, 4, 8, 8

How to calculate Baesian average for item 2:

avg_num_votes = 2.333   //The average number of votes for all items (1+3+4) / 3

avg_rating = 8.5 //The average rating for all items (10+9+10+9+10+4+8+8) / 8

item_num_votes = 3  //The number of votes for current item (Item 2) 

item_rating = 9.33     //The average rating for current item (Item 2): (9+10+9)/3
 
bayesian_average = 8.941 // ((avg_num_votes * avg_rating) + (item_num_votes * item_rating)) / (avg_num_votes + item_num_votes)
                    
Averages:
                    
Element 1: 8.909        

Element 2: 8.941

Element 3: 7.9

You can see although Hamlet has an 10, and Cicero has two 9's and one 10 the baesian average of Cicero is the highest

Sample data in baesian collection document:
````
{
	"_id" : 2,
	"name" : "Cicero",
	"marks" : [
		{
			"userid" : 5,
			"mark" : 9
		},
		{
			"userid" : 3,
			"mark" : 10
		},
		{
			"userid" : 2,
			"mark" : 9
		}
	],
	"nr_votes" : 3,
	"sum_votes" : 27
}
````

Swagger url: http://localhost:84/apidocs

Using Curl:

To create an item:
````
curl -X POST -i "http://localhost:84/item/3" -d name=some_name
````

To vote an item:

ex: user with id 9 votes item 3 with mark 8

````
curl -X PUT -i "http://localhost:84/item/vote/3" -d mark=8 -d userid=9
````

To get an item, along with it's average:

````
curl -i "http://localhost:84/item" 
````

# Photo process

In this usecase we'll use docker volumes to map the local folder called "container-storage" inside the Docker image.

The python webserver will write / delete images in this folder.

One interesting feature of this api is to search similar images. For example you cand take one photo from the 
container-storage folder, rename it, and modify the brightness or slightly crop it and then try to find it using the API.

To achive this the script will load all images from disk, hash them using a hasing function and compare the hash differences.
It's only a naive implementation for demo purposes, it's main drawbacks are memory limit (all hashes should fit in memory)
and linear search times, the complexity of the search it's linear with the number of photo hashed and saved.


The API will expose methods for adding and deleting images along with resizing and rotating and search by similar image

Swagger url: http://localhost:85/apidocs

Api methods using Curl:

To get image with id 1, and rezise it by height 100
````
curl -i "http://localhost:85/photo/1?resize=100"
````

To delete image with id 1:
````
curl -X DELETE http://localhost:85/photo/1
````

To add a image with id 1:
````
curl -X PUT -F "file=@image.jpg" http://localhost:85/photo/1
````

To search images similar with a given one:
````
curl -X PUT -F "file=@image.jpg" http://localhost:85/photo/similar
````

# Book-collection

Still some refinements should be made to the api, and the documentation below enhanced:

- use transactions when borrow and return a book (this requires a MongoDb cluster, it will be added in the future)


A book library. Users must be defined using the Users CRUD service. Book profiles can be created through the API. 
Books can be borrowed and an accounting mechanism for this is in place.

Uses Flask Restplus: https://flask-restplus.readthedocs.io

The Swagger is http://localhost:86

Api methods using Curl:
 
Add a book:
````
curl -X PUT "http://localhost:86/book/978-1607965503" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"isbn\": \"978-1607965503\", \"name\": \"Lincoln the Unknown\", \"author\": \"Dale Carnegie\", \"publisher\": \"snowballpublishing\", \"nr_available\": 5}"

````
Get a book:
````
curl -i "curl -X GET "http://localhost:86/book/978-1607965503" -H "accept: application/json"" 
````

List all books:
````
curl -X GET "http://localhost:86/book?limit=5&offset=0" -H "accept: application/json" 
````

Delete a book:
````
curl -X DELETE "http://localhost:86/book/1" -H "accept: application/json"
````

Borrow book:
````
curl -X PUT "http://localhost:5000/borrow/1" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"id\": \"1\", \"userid\": 4, \"isbn\": \"978-1607965503\", \"borrow_date\": \"2019-12-12T09:32:51.715Z\", \"return_date\": \"2020-02-12T09:32:51.715Z\"}"
````

List a book borrow:
````
curl -X GET "http://localhost:86/borrow/1" -H "accept: application/json"
````

List all book borrows:
````
curl -X GET "http://localhost:86/borrow?limit=2&offset=0" -H "accept: application/json"
````

Return a book:
````
curl -X PUT "http://localhost:86/borrow/return/16" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"id\": \"16\", \"return_date\": \"2019-12-13T08:48:47.899Z\"}"
````

# Grafana and InfluxDb

Grafana with InfluxDb integration for displaying sensor data. the MQTT service sends datapoints to InfluxDb and Grafana displays the metrics.

The Grafana web interface is abailable at: http://localhost:3000 

The grafana API methods are available here: https://grafana.com/docs/grafana/latest/http_api/

The grafana docker image creates a dashboard called "SensorMetrics", so in the interface go to home and select it.

Inserting humidity datapoint with value 61 data directly into the InfluxDb database:
````
curl -i -XPOST 'http://localhost:8086/write?db=influx' --data-binary 'humidity value=61'
````

Inserting humidity datapoint with value 61 using MQTT:
````
mosquitto_pub -h localhost -u some_user -P some_pass -p 1883 -d -t sensors -m "{\"sensor_id\": \"humidity\", \"sensor_value\": 61}"
````

After you have inserted some datapoints, to view the graphs first select the "SensorMetrics", then from the top right corner
select "Last 5 minutes" and from sensortype selectbox type the sensor name (the one you inserted datapoints for) like "humidity".


To connect to your local InfluxDb instance use for debug or for fun:
````
docker ps
````
You should get something like: 
````
CONTAINER ID        IMAGE                                   COMMAND                  CREATED             STATUS              PORTS                                        NAMES
2dbf0b749e17        web-mqtt-image                          "python ./flask-mong…"   26 hours ago        Up 26 hours         5000/tcp                                     docker-flask-mongodb-example_web-mqtt_1
1fa1be6ab050        web-baesian-image                       "python ./flask-mong…"   26 hours ago        Up 26 hours         0.0.0.0:84->5000/tcp                         docker-flask-mongodb-example_web-baesian_1
d40f5ef73695        web-random-image                        "python ./flask-mong…"   26 hours ago        Up 26 hours         0.0.0.0:800->5000/tcp                        docker-flask-mongodb-example_web-random_1
2d368aedf1da        web-photo-image                         "python ./flask-mong…"   26 hours ago        Up 26 hours         0.0.0.0:85->5000/tcp                         docker-flask-mongodb-example_web-photo-process_1
841ed17fbf6a        web-users-image                         "python ./flask-mong…"   26 hours ago        Up 26 hours         0.0.0.0:81->5000/tcp                         docker-flask-mongodb-example_web-users_1
469e0c6388a5        web-fulltext-image                      "python ./flask-mong…"   26 hours ago        Up 26 hours         0.0.0.0:82->5000/tcp                         docker-flask-mongodb-example_web-fulltext-search_1
2b81e8eda0a4        web-geolocation-image                   "python ./flask-mong…"   26 hours ago        Up 26 hours         0.0.0.0:83->5000/tcp                         docker-flask-mongodb-example_web-geolocation-search_1
764b415b2988        docker-flask-mongodb-example_grafana    "/app/entrypoint.sh"     26 hours ago        Up 26 hours         0.0.0.0:3000->3000/tcp                       docker-flask-mongodb-example_grafana_1
d585a73657c6        mongo:4.2-bionic                        "docker-entrypoint.s…"   26 hours ago        Up 26 hours         0.0.0.0:27017->27017/tcp                     docker-flask-mongodb-example_mongo_1
33d4dec53354        devopsfaith/krakend                     "/usr/bin/krakend ru…"   26 hours ago        Up 26 hours         8000/tcp, 8090/tcp, 0.0.0.0:8080->8080/tcp   docker-flask-mongodb-example_krakend_1
035124f1b665        docker-flask-mongodb-example_influxdb   "/app/entrypoint.sh"     26 hours ago        Up 26 hours         0.0.0.0:8086->8086/tcp                       docker-flask-mongodb-example_influxdb_1
7240b808bfb1        docker-flask-mongodb-example_mqtt       "/docker-entrypoint.…"   26 hours ago        Up 26 hours         0.0.0.0:1883->1883/tcp                       docker-flask-mongodb-example_mqtt_1
````
Now lunch the influx shell inside the container replacing 035124f1b665 with your own container id like so:

````
docker exec -it 035124f1b665 influx
````
And you're inside the influx shell, and you can issue commands, some examples here: https://docs.influxdata.com/influxdb/v1.7/introduction/getting-started/ 
