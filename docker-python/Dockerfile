FROM python:3.8-buster

ARG requirements
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
WORKDIR /root/flask-mongodb-example/python
RUN pip install -qr $requirements

EXPOSE 5000