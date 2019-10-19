FROM python:3.7-stretch

ARG requirements
RUN apt-get update

WORKDIR /root
RUN mkdir flask-mongodb-example
COPY ./ ./flask-mongodb-example/
COPY ./python/* ./flask-mongodb-example/
RUN pip install -qr $requirements

EXPOSE 5000