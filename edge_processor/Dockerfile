FROM python:2.7-slim

WORKDIR /usr/src/edge_processor

COPY . .

#RUN apt-get update && apt-get install -y stress-ng
RUN apt-get update

RUN pip install -r requirements.txt

#ENTRYPOINT [ "python", "./stream_process.py" ]
ENTRYPOINT [ "python", "./stream_wifi.py" ]
