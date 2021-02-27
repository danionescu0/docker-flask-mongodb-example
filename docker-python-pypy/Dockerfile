FROM pypy:3-slim
ARG requirements
RUN apt-get update
RUN apt install git -y
WORKDIR /root
RUN git clone https://github.com/danionescu0/docker-flask-mongodb-example.git flask-mongodb-example
WORKDIR /root/flask-mongodb-example/python
RUN pip install -qr $requirements
EXPOSE 5000
