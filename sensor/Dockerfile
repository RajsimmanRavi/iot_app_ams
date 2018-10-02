FROM python:3.5

WORKDIR /usr/src/send_data

COPY . .

RUN pip3 install -r requirements.txt 

ENTRYPOINT [ "python", "./send_wifi_data.py" ]
#ENTRYPOINT [ "python", "./send_wifi_data_vRand.py" ]
