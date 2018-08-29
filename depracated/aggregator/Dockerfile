FROM python:2.7-slim

WORKDIR /usr/src/aggregator

COPY . .

RUN pip install --no-cache-dir kafka-python

RUN pip install --no-cache-dir cassandra-driver

ENTRYPOINT [ "python", "./aggregate.py" ]
