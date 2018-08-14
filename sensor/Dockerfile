FROM python:3.4-slim

WORKDIR /usr/src/send_data

COPY . .

RUN pip3 install -r requirements.txt 


ENTRYPOINT [ "python", "./send_wifi_data.py" ]
#ENTRYPOINT [ "python", "./send_data.py" ]
#CMD [ "python", "./send_data.py", "10.12.1.76", "2181" ]
#RUN python ./send_data.py $IP $PORT
