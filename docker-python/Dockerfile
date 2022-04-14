FROM web-base
# web-base is the Dockerfile inside ./base folder, it's splitted in 2 to speed up the multiple image build process

ARG requirements

WORKDIR /root/flask-mongodb-example/python
ENV PYTHONPATH "/root/flask-mongodb-example/python/common"
RUN pip install -qr $requirements

EXPOSE 5000