FROM python:3.9-buster

ARG requirements
RUN apt-get update
RUN apt-get install -y gfortran libopenblas-dev liblapack-dev
RUN pip install cython

WORKDIR /root
RUN mkdir flask-mongodb-example
COPY ./ ./flask-mongodb-example/
COPY ./python/* ./flask-mongodb-example/

RUN pip install -qr $requirements

EXPOSE 5000