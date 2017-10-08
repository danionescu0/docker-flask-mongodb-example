## Purpose
Uses docker-compose with a python flask microservice and mongodb instance to make two sample applications
- one that generates random numbers and lists them
- and the other CRUD (create, read, update, delete) application over a user collection

The applications will run in paralel using docker-compose, 
the random_demo will run on port 80 and the crud on port 81

## Technollogies involved
[Docker](https://opensource.com/resources/what-docker), [docker-compose](https://docs.docker.com/compose/), [python](https://www.python.org/doc/essays/blurb/), [flask microframework](http://flask.pocoo.org/)

* How to install docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04
* How to install docker compose: https://docs.docker.com/compose/install/


## Run the microservice
docker-compose up

## Using the microservice
After we start the server using the command above, we'll be testing 
the requests using linux [curl][https://curl.haxx.se/docs/manpage.html]


1) Random service

The random number collection has only one documents with '_is' lasts
and an "items" key that will be a capped array

* Generate a random number between 10 and 100: 
````
curl -i "http://localhost/random/10/100"
````

* View last 5 generated numbers list: 

````
curl -i "http://localhost/random-list"
````

2) CRUD service

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

*DELETE request, this request will delete a unser with a specified id

example for with id 1:
````
curl -X DELETE -i "http://localhost:81/users/1"
````