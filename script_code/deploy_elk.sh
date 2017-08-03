#!/bin/bash

# Check if arguments given
if [[ $# -eq 0 ]] ; then
    echo "Error: you need to provide the IP address of Elasticsearch's Host"
    exit 1
fi

SCRIPTS_DIR="/home/ubuntu/Elascale"
ELK_DIR="$SCRIPTS_DIR/elk"
ELASTIC_IP="$1"

#Now, replace the url in ek-compose.yml to the ELASTIC_IP
sed -i "s/ELASTICSEARCH_URL=.*/ELASTICSEARCH_URL=http:\/\/$ELASTIC_IP:9200/g" $ELK_DIR/ek-compose.yml
        
echo "Deploying EK services"

sudo docker stack deploy -c $ELK_DIR/ek-compose.yml EK_monitor

echo "Waiting for Elasticsearch to be up and running"

$SCRIPTS_DIR/sleep_bar.sh 60

echo "Done waiting! Importing Dashboards and templates"

elasticdump --input=$ELK_DIR/dash_templates/index_analyzer.json --output=http://$ELASTIC_IP:9200/.kibana --type=analyzer
elasticdump --input=$ELK_DIR/dash_templates/index_mapping.json --output=http://$ELASTIC_IP:9200/.kibana --type=mapping
elasticdump --input=$ELK_DIR/dash_templates/index_data.json --output=http://$ELASTIC_IP:9200/.kibana --type=data

echo "Completed ELK deployment"
