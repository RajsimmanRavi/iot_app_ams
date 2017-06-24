FROM python:2.7-slim

WORKDIR /usr/src/edge_processor

COPY . .

RUN apt-get update && apt-get install -y stress-ng

RUN pip install --no-cache-dir kafka-python

RUN pip install --no-cache-dir cassandra-driver

ENTRYPOINT [ "python", "./stream_process.py" ]
