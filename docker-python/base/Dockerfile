FROM python:3.10-buster as web-base

#[DEVELOPMENT ONLY] run in shell from root location
# mkdir docker-python/base/project; rsync -av --progress ./ docker-python/base/project --exclude docker-python

# this is the python base image that contains olny git and the downloaded project
RUN apt-get update
RUN apt install git -y

WORKDIR /root

# 1. [DEVELOPMENT ONLY] uncomment the following 2 lines (will copy files from local instead from github)
# RUN mkdir flask-mongodb-example
# COPY ./project ./flask-mongodb-example/

# 2. [DEVELOPMENT ONLY] comment the line with git clone
RUN git clone https://github.com/danionescu0/docker-flask-mongodb-example.git flask-mongodb-example
