FROM python:2.7

WORKDIR /usr/src/edge_processor

COPY . .

#RUN apt-get update && apt-get install -y stress-ng
RUN apt-get update 

#RUN apt-get install -y build-essential

#RUN apt-get install -y python3-mysqldb python3-mysqldb-dbg 

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "./stream_wifi.py" ]
