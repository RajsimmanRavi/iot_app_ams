FROM python:2.7-slim

WORKDIR /usr/src/send_data

COPY . .

RUN pip install --no-cache-dir kafka-python

ENTRYPOINT [ "python", "./send_data.py" ]
#CMD [ "python", "./send_data.py", "10.12.1.76", "2181" ]
#RUN python ./send_data.py $IP $PORT
