# iot_app_cascon

Simple IoT Appplication for CASCON
----------------------------------

This is a simple application created for CASCON. It resembles an architecture that can be utilized in IoT environments. Docker images have been used for this application. Hence, you don't need to build anything from scratch. However, you need to change some hard-coded IP Addresses (and/or ports) in iot_app.sh and docker-compose.yml files.

There are 4 main services in this application. 
  * **Sensor**: This collects CPU, memory and network stats of the container itself (agreed that it's not useful). <br /> It also sends data to Kafka (as a Producer) under topic 'stats' (already created by Kafka service on boot) every 15 secs.
  * **Aggregator**: There are three key funcationalities:
    * It starts a Kafka consumer and starts listening for incoming data under 'stats' topic
    * It also initializes the Cassandra database (creates keyspace 'stats' and table 'data')
    * Any incoming data will be automatically sent to Cassandra database
  * **Kafka (and Zookeeper)**: This service brings the Zookeeper and Kafka broker up and running. It also creates the topic 'stats' on start up.
  * **Cassandra**: This service simply brings up the Cassandra database.
  
### Instructions for deployment ###
The neatness of this application is that it requires minimal pre-requisites. As long as there is a docker swarm with three nodes, this application can be brought up with minimal configuration <br />
**However**, you have to make some changes to **docker-compose.yml** and **iot_app.sh** files. Pay particular attention to **IP addresses, ports, and node labels** and make necessary changes. <br />
Hence, you mainly need the following files: **docker-compose.yml, iot_app.sh and clean.sh**

Once those changes have been made, you simply have to call the **./iot_app.sh**, and it will bring all the services.<br />
As you may have guessed, **clean_up.sh** removes all the services.
 
The aggregator and sensor docker images can be found in the docker hub links (shown below):
  * Sensor image: https://hub.docker.com/r/perplexedgamer/sensor/
  * Aggregator image: https://hub.docker.com/r/perplexedgamer/aggregator/

You can find the details of those images on the docker-hub description. 

For reference purposes, the python files (for both Sensor and Aggregator) are in this repository. If updates need to be made, you can run the conatiner and start making changes.
Note: Make sure you save the image before exit. Otherwise all changes will be lost.

I've also included the Dockerfiles (for both of them). You don't need these files to get the images, but they merely serve for reference purposes.


