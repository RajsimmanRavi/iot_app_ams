#!/bin/bash

docker stack rm iot_app

sleep 1

echo -e "Removing service iot_sensor"

docker service rm iot_sensor

sleep 1

echo -e "Removing service iot_edge_processor"

docker service rm iot_edge_processor

sleep 1

echo -e "Removing service visualize-cluster"

docker service rm visualize-cluster

sleep 1 

echo -e "Removed all services!\n"

sleep 1

echo -e "Services status: " 

docker service ls
