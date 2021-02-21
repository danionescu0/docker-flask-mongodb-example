FROM python:3.8-buster as web-base
# this is the python base image that contains olny git and the downloaded project
RUN apt-get update
RUN apt install git -y

WORKDIR /root

#development only
#1. uncomment the following 2 lines (will copy files from local instead from github
#2 comment the line with git clone
#2. run in shell from Dockerfile location: mkdir project; rsync -av --progress ../ ./project/ --exclude docker-python
#RUN mkdir flask-mongodb-example
#COPY ./project ./flask-mongodb-example/


RUN git clone https://github.com/danionescu0/docker-flask-mongodb-example.git flask-mongodb-example