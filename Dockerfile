FROM python:3.5-jessie


RUN apt-get update
WORKDIR /root
RUN mkdir flask-mongodb-example
COPY ./ ./flask-mongodb-example/
RUN cat ./flask-mongodb-example/requirements.txt
RUN pip install -qr ./flask-mongodb-example/requirements.txt

ENTRYPOINT ["python", "./flask-mongodb-example/random_demo.py"]
EXPOSE 5000