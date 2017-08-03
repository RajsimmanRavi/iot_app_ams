#!/bin/bash

SCRIPTS_DIR="/home/ubuntu/Elascale"
ELASTIC_IP=`$SCRIPTS_DIR/./get_elastic_ip.sh`
HOSTNAME=`hostname`
HOST_IP=`ifconfig ens3 | grep 'inet addr' | cut -d ':' -f 2 | awk '{print $1}'`

$SCRIPTS_DIR/./deploy_elk.sh $ELASTIC_IP

echo "Deployed Elasticsearch and Kibana. Preparing Beats configuration"

$SCRIPTS_DIR/./sleep_bar.sh 20

echo "Starting Beats deployment"

$SCRIPTS_DIR/./deploy_beats.sh $ELASTIC_IP

#Let's create the Elascale UI
echo "Deployed Beats. Starting Elascale service UI "

sleep 2

#Ok, this docker service command is huge. Let's break it down
# -p 8888:8888 - bind the host port to the container port 
# --detach=true - detach the service and run it in background
# --constraint node.hostname==$HOSTNAME - run it on this host only
# --mount=type=bind,src=$SCRIPTS_DIR/conf,dst=$SCRIPTS_DIR/conf - bind the host's folder to the container, such that changes made to this folder (by the container) will be used by the host as well
# --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock - bind the docker sock to get docker client information from inside the container
# perplexedgamer/ui - container image
# The remaining flags are args to the image 

sudo docker service create -p 8888:8888 --detach=true --name ui --constraint node.hostname==$HOSTNAME --mount=type=bind,src=$SCRIPTS_DIR/conf,dst=$SCRIPTS_DIR/conf --mount=type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock perplexedgamer/ui --host_ip=$HOST_IP --elastic_ip=$ELASTIC_IP --micro=$SCRIPTS_DIR/conf/microservices.ini --macro=$SCRIPTS_DIR/conf/macroservices.ini

