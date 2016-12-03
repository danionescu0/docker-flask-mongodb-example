FROM ubuntu:14.04
RUN apt-get update && apt-get install -y -q python-all python-pip
COPY requirements.txt /var/local/
RUN pip install -qr /var/local/requirements.txt
COPY server.py /var/local/
RUN pip install -qr /var/local/requirements.txt
WORKDIR /var/local
EXPOSE 5000
CMD ["python", "server.py"]
