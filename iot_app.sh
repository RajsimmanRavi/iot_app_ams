#!/bin/bash

docker stack deploy -c /home/ubuntu/iot_app/docker-compose.yml iot_app

echo -e "\nDeployed Kafka, Zookeeper and Cassandra! Starting Sensor and Aggregator in a few secs..."

sleep 5

docker service create --replicas 1 --name iot_sensor --constraint node.labels.loc==agg-sensor perplexedgamer/sensor 10.12.1.42 9092

docker service create --replicas 1 --name iot_agg --constraint node.labels.loc==agg-sensor perplexedgamer/aggregator 10.12.1.42 10.12.1.24

echo -e "\nDeployed Sensor and Aggregator! IoT Application deployment complete! Starting Visualizer service..."

sleep 2 

docker service create --name=visualize-cluster --publish=5000:8080/tcp --constraint=node.role==manager  --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock manomarks/visualizer

echo -e "\n Created UI. You can visit http://10.12.1.48:5000 to view the dashboard!"

sleep 2 

echo -e "Current services status:\n"

docker service ls 

sleep 1

echo -e "\nWait for all the services to be up and running (i.e. Replicas: 1/1)\n"

sleep 2 

echo -e "You can log into Cassandra container (from iot-core VM) to view stored data by performing following steps:\n"

sleep 2

echo -e "$ docker exec -it {cassandra_db_container_id} cqlsh"
echo -e "> select * from stats.data;"
