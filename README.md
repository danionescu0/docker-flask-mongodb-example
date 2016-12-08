## Purpose
Uses docker-compose with a python flask microservice and mongodb instance to make a sample application
that generates random numbers and lists them.

## Technollogies involved
[Docker](https://opensource.com/resources/what-docker), [docker-compose](https://docs.docker.com/compose/), [python](https://www.python.org/doc/essays/blurb/), [flask microframework](http://flask.pocoo.org/)

* How to install docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04
* How to install docker compose: https://docs.docker.com/compose/install/

## Specifications
* The api will provide a url for generating a random number between a and b,
where b>=a.
* We'll also provide a url for listing the last 5 generated numbers

## Run the microservice
docker-compose up

## Access the microservice
* generate a random number between 10 and 100: "http://localhost/random/10/100"
* view last 5 generated numbers list: "http://localhost/random-list"

