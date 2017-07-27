import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options
import ConfigParser
import docker
import os
import json 
import argparse 

#Simple explanation of the required commandline arguments
parser = argparse.ArgumentParser(description="*** Elascale UI ***")
parser.add_argument('--host_ip', help='IP address of the host this service is running on', type=str)
parser.add_argument('--kibana_link', help='Short URL of Kibana dashboard', type=str)
args = parser.parse_args()


#Commandline arguments
define("host_ip", default="10.11.1.7", help="The host's IP address")  
define("kibana_link", default="http://kibana_ip_not_provided",help="The short URL to the Kibana dashboard")
define("port", default = 8888, help = "port to run on", type = int) # This is for final version

""" 
    Function to read the Config ini file and return that variable. 
"""
def read_file(f_name):
    Config = ConfigParser.ConfigParser()
    Config.read(f_name)
    
    return Config

""" 
    Function to insert modified values to the appropriate config ini file (micro or macro). 
    Returns nothing. If error occurs, the try/except on the called function will catch the error

    The argument is the received data from client/browser end. The format is in json:
    {"service_type": "xx", "service": "xx", "${config_param}": "xx" ...}

    service_type: defines whether it's a micro-service or macro-service
    service: define what service is getting modified (i.e. iot_app_cass, iot_edge_processor etc.)
    The other keys are basically the config_params (eg. cpu_up_lim, max_replica etc.)
    The corresponding values are the newly modified values that needs to be written to file.
"""
def write_file(data):
    Config = ConfigParser.ConfigParser()

    #Convert string to json 
    data = json.loads(data) 
   
    service_type = data["service_type"] # Tells us whether 'micro' or 'macro' 
    service = data["service"]

    f_name = "/home/ubuntu/Elascale/conf/"+service_type+"services.ini"
    Config.read(f_name)
    
    #delete service_type and service keys from dict
    del data["service_type"]
    del data["service"]

    for key, value in data.iteritems():
  
        # Set appropriate values
        Config.set(service,key,value)
        
    #Write the changes to file
    with open(f_name, 'wb') as configfile:
        Config.write(configfile)
        
"""
    Function to get the current macro-services (VMs) from the docker client. 
    It creates a list and returns it 
"""
def get_macro(client):

    nodes = client.nodes.list()
    macro_services = []

    for node, val in enumerate(nodes):
        try:
            loc = nodes[node].attrs['Spec']['Labels']['loc']
        except KeyError:
            continue # Goes back to the beginning of for loop
        else:
            macro_services.append(nodes[node].attrs['Description']['Hostname'])

    return macro_services

"""
    Function to get the current micro-services from the docker client. 
    It creates a list and returns it 
"""
def get_micro(client):

    services = client.services.list()
    micro_services = []

    for serv, val in enumerate(services):

        if ((bool(services[serv].attrs['Spec']['Labels']) == False) or (services[serv].attrs['Spec']['Labels']['com.docker.stack.namespace'] == "iot_app")):
            micro_services.append(services[serv].attrs['Spec']['Name'])

    return micro_services

"""
    Function to get the final list of services such that UI only shows the INI file's services
    Although redundant, this is to make sure that only these services are shown.  
"""
def get_final_list(running_services, config_services):

    config_serv_sections = config_services.sections() #ConfigParser sections are the services 

    final_list = []

    for serv in running_services:
        if serv in config_serv_sections:
            final_list.append(serv)

    return final_list

"""
   Class to handle the /config.
   Basically writes the new values to the appropriate ini file.
   Returns the success/error msg.
"""
class ConfigHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Websocket opened")

    def on_message(self, message):
        
        try: 
            write_file(message)
        except Exception as e:
            self.write_message(str(e))
        else:
            self.write_message("Values have been modified successfully! Press OK to view changes")

    def on_close(self):
        print("Websocket closed")

"""
    Class to handle / .
    Basically calls the get_micro and get_macro to fetch the current running services and VMs.
    Then, it reads the ini files to get their current config parameter values. 
    It sends them both to index.html to render that content.
"""

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        client = docker.from_env()
	
        micro = get_micro(client)
	macro = get_macro(client)
	
        # Read ini files
        micro_config = read_file("/home/ubuntu/Elascale/conf/microservices.ini")
        macro_config = read_file("/home/ubuntu/Elascale/conf/macroservices.ini")

        # Make sure only micro and macro services that are on the ini files are sent. 
        # I.E., don't get all the services running and blindly send it.
        micro = get_final_list(micro,micro_config)
        macro = get_final_list(macro, macro_config)

	#Get the IP address of the server from the Commandline argument   
        ip_addr = options.host_ip

        #Get the Kibana short URL from the Commandline argument
        kibana_link = options.kibana_link

        print(kibana_link)
        
        self.render("index.html", micro_services=micro, macro_services=macro, micro_config=micro_config, macro_config=macro_config, ip_addr=ip_addr, kibana_link=kibana_link)

class Application(tornado.web.Application):
    def __init__(self):
    	"""
	initializer for application object
	"""
    	handlers = [
	    (r"/", MainHandler),
	    (r"/config", ConfigHandler),
	]

	settings = {
	    "debug": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
	}
     
	tornado.web.Application.__init__(self,handlers,**settings)


def main():
    if args.host_ip is None or args.kibana_link is None:
        print("Wrong Usage. Please use -h or --help flag for proper arguments")
    else:
        tornado.options.parse_command_line()
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(options.port) # This is for the final version
        tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
