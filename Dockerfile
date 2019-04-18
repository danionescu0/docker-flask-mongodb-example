FROM python:3.7-stretch


RUN apt-get update

WORKDIR /root
RUN mkdir flask-mongodb-example
COPY ./ ./flask-mongodb-example/
COPY ./python/* ./flask-mongodb-example/
RUN pip install -qr ./flask-mongodb-example/requirements.txt

ENTRYPOINT ["python", "./flask-mongodb-example/random_demo.py"]
EXPOSE 5000