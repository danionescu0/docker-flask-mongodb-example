## Purpose

**A working demo usage of docker, docker-compose, mongodb, python3, docker-compose, mosquitto:**

**1** usecase an api that generates random numbers and lists them

**2** one deals with crud operations CRUD (create, read, update, delete) 
application over a user collection

**3** will use a MQTT server (Mosquitto) to allow to publish sensor updates over MQTT
The updates will be saved in mongodb (/demo/sensors). It will also compute a running average 
for each sensor and publish it to a separate topic

**4** fulltext search engine backed by fulltext mongoDb index

**5** geospacial search service that supports adding places, and quering the placing by coordonates and distance



The applications will run in parallel using docker-compose

1. random_demo will run on port 80
2. the crud on port 81
3. MQTT service will run on default port 1883
4. fulltext_search will run on port 82
5. geospacial search service will rund on port 83

Before running check that the ports are available and free on your machine!

![diagram.png](https://github.com/danionescu0/docker-flask-mongodb-example/blob/master/resources/diagram.jpg)

## Technollogies involved
[Docker](https://opensource.com/resources/what-docker), [docker-compose](https://docs.docker.com/compose/), 
[python](https://www.python.org/doc/essays/blurb/), 
[flask microframework](http://flask.pocoo.org/)
[Mosquitto MQTT] (https://mosquitto.org/)
[Curl] (https://curl.haxx.se/)

* How to install docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04
* How to install docker compose: https://docs.docker.com/compose/install/



## Run the microservice
````
docker-compose up
````

## Using the microservice
For applications 1 and 2 after we start the server using the command above, we'll be testing 
the requests using linux [curl][https://curl.haxx.se/docs/manpage.html]

For the application 3 we'll be using mosquitto cli to test the pub-sub it's working

To install mosquitto cli tool:
````
sudo apt-get install mosquitto-clients
````


1) **Random service**

The random number collection has only one documents with '_is' lasts
and an "items" key that will be a capped array
MongoDb official documentation (array operations): https://docs.mongodb.com/manual/reference/operator/update/slice/
* Generate a random number between 10 and 100: 
````
curl -i "http://localhost/random/10/100"
````

* View last 5 generated numbers list: 

````
curl -i "http://localhost/random-list"
````

2) **CRUD service**

The user collections contains _id which is the userid, a name and a email:


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

3) **MQTT service**

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


4) **Fulltext service**

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

5) **Geospacial search service **

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