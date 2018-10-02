IoT Appplication for Autonomic Management System
----------------------------------

This is an application created for testing the Autonomic Management System (AMS) on SAVI Testbed. For more information, please refer to this: https://github.com/RajsimmanRavi/Elascale_secure. It resembles an architecture that can be utilized in IoT environments. Docker images have been used for this application. Hence, you don't need to build anything from scratch. However, you need to edit iot_app_compose.yml to resemble your deployment (either 1 machine or distributed platform). 

There are 4 main services in this application. 
  * **Sensor**: We collected some real environment WiFi capture during a festival. We processed the PCAP files and removed any sensitive material and kept only processed WiFi Probe request data. This service basically replays the stream in a randomized manner. It sends the data to a REST API using (POST).
  * **REST API**: There are three key funcationalities:
    * Initializes the MySQL database (creates keyspace 'wifi' and table 'data')
    * Listens on port **6969** for any incoming data (using POST). It will parse the data and insert it into MySQL database
    * Can also provide top manufacturers (based on MAC addresses of inserted data in database). You can do a GET request: /get_data
  * **Database**: This service simply brings up the MySQL database (Repuires port **3306**)
  
### Instructions for deployment ###
The neatness of this application is that it requires minimal pre-requisites (as long as it is deployed on Docker Swarm master). Once you've made the necessary changes to iot_app_compose.yml, you can deploy the application as a stack: 

``` sudo docker deploy -c iot_app_compose.yml iot_app ```

You can remove the application stack using the following command: 

``` sudo docker stack rm iot ```
 
The aggregator and sensor docker images can be found in the docker hub links (shown below):
  * Sensor image: https://hub.docker.com/r/perplexedgamer/sensor/
  * REST API image: https://hub.docker.com/r/perplexedgamer/rest_api/

You can find the details of those images on the docker-hub description. 

For reference purposes, the source code for both Sensor and REST API is in this repository. If updates need to be made, you can run the conatiner and start making changes.
Note: Make sure you save the image before exit. Otherwise all changes will be lost.

I've also included the Dockerfiles (for both of them). You don't need these files to get the images, but they merely serve for reference purposes.

Any questions/concerns/issues/feedback is greatly appreciated! Contact: rajsimmanr@gmail.com
