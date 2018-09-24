FROM python:2.7

WORKDIR /usr/src/rest

COPY . .

#RUN apt-get update && apt-get install -y stress-ng
RUN apt-get update 

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "./api.py" ]
