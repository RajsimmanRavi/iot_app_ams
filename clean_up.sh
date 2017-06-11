#!/bin/bash

docker stack rm iot_app

sleep 1

echo -e "Removing service iot_sensor"

docker service rm iot_sensor

sleep 1

echo -e "Removing service iot_agg"

docker service rm iot_agg

sleep 1

echo -e "Removing service visualize-cluster"

docker service rm visualize-cluster

sleep 1 

echo -e "Removed all services!\n"

sleep 1

echo -e "Services status: " 

docker service ls
