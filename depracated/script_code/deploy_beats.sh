#!/bin/bash

# Raj: Making it a little dynamic -- zziing!! No offence Byungchul

#sudo docker run -d --hostname $(hostname) --name=dockbeat.$(hostname) -v /var/run/docker.sock:/var/run/docker.sock -v ~/dockbeat.yml:/etc/dockbeat/dockbeat.yml -v /volumes/dockbeat-logs/:/var/logs/dockbeat ingensi/dockbeat
#sudo docker run -d --name=metricbeat.$(hostname) -v ~/metricbeat.yml:/usr/share/metricbeat/metricbeat.yml --volume=/proc:/hostfs/proc:ro --volume=/sys/fs/cgroup:/hostfs/sys/fs/cgroup:ro --volume=/:/hostfs:ro --net=host docker.elastic.co/beats/metricbeat:5.4.1 metricbeat -e -system.hostfs=/hostfs

# Check if arguments given
if [[ $# -eq 0 ]] ; then
    echo "Error: you need to provide the IP address of Elasticsearch's Host"
    exit 1
fi

ELASTIC_IP="$1"
BEATS_DIR="/home/ubuntu/Elascale/beats"
DOCKBEAT_DIR="$BEATS_DIR/dockbeat"
METRICBEAT_DIR="$BEATS_DIR/metricbeat"
THIS_NODE_HOSTNAME=`hostname`

# Ok, the command is huge. Let me break it down.
# "docker node ls" gives us the nodes and it's hostnames.
# awk {print $2" "$3} gives us only the hostnames.
# sed 's/*//g' removes the asterisk
# sed 's/Ready//g' removes the string "Ready" because we had that when we printed $3
# sed 's/HOSTNAME//g' removes the string "HOSTNAME" from the title of the output
# sed 's/STATUS//g' removes the string "STATUS" from the title of the output
# sed '/^$/d'` removes empty lines from the output

# Hence this provides only the hostnames of the nodes we want to deploy dockbeat and metricbeat.
# Store this in an array
NODES=( $(sudo docker node ls | awk '{print $2}' | sed 's/*//g' | sed 's/Ready//g' |sed 's/HOSTNAME//g' | sed 's/STATUS//g'| sed '/^$/d') )

# Let's start with the dockbeat. First replace ELASTIC_IP with the 1st argument
sed -i "s/hosts: \[\".*:9200\"\]/hosts: \[\"$ELASTIC_IP:9200\"\]/g" $DOCKBEAT_DIR/dockbeat.yml

# Then, let's do the same for metricbeat. 
sed -i "s/hosts: \[\".*:9200\"\]/hosts: \[\"$ELASTIC_IP:9200\"\]/g" $METRICBEAT_DIR/metricbeat.yml

for hostname in "${NODES[@]}"
do
    # Let's replace name in metricbeat.yml
    # Replace `name: "*"` with `name: "hostname"`
    sed -i "s/name: \".*\"/name: \"$hostname\"/g" $METRICBEAT_DIR/metricbeat.yml

    # send the files to the node
    sudo docker-machine scp $DOCKBEAT_DIR/dockbeat.yml $hostname:~
    sudo docker-machine scp $METRICBEAT_DIR/metricbeat.yml $hostname:~

    # we also need to make sure /volumes/dockbeat-logs/ is in each node
    sudo docker-machine ssh $hostname 'mkdir -p /volumes/dockbeat-logs' 
    
    echo "Done sending files for node: $hostname"
done

#We still need to do it for this node itself
sed -i "s/name: \".*\"/name: \"$THIS_NODE_HOSTNAME\"/g" $METRICBEAT_DIR/metricbeat.yml

#Copy it to the home folder 
cp $DOCKBEAT_DIR/dockbeat.yml ~
cp $METRICBEAT_DIR/metricbeat.yml ~

echo "Done putting files to the home folder for this node: $THIS_NODE_HOSTNAME"

echo "Deploying Beats...by Dr.Dre...No, just Metricbeat and Dockbeat"

sleep 2 

sudo docker stack deploy -c $BEATS_DIR/beat-compose.yml beats
