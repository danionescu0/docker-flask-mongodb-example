FROM python:3.8-buster as web-base
# this is the python base image that contains olny git and the downloaded project
RUN apt-get update
RUN apt install git -y

WORKDIR /root

# [DEVELOPMENT ONLY]

# 1. [DEVELOPMENT ONLY] uncomment the following 2 lines (will copy files from local instead from github)
# RUN mkdir flask-mongodb-example
# COPY ./project ./flask-mongodb-example/

# 2. [DEVELOPMENT ONLY] comment the line with git clone
RUN git clone https://github.com/danionescu0/docker-flask-mongodb-example.git flask-mongodb-example

# 3. [DEVELOPMENT ONLY] run in shell from Dockerfile location: mkdir project; rsync -av --progress ../../ ./project/ --exclude docker-python