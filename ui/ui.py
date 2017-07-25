import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options
import ConfigParser
import docker
import os

define("port", default = 8888, help = "port to run on", type = int) # This is for final version

def read_file(f_name):
    Config = ConfigParser.ConfigParser()
    Config.read(f_name)
    
    return Config
 
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

def get_micro(client):

    services = client.services.list()
    micro_services = []

    for serv, val in enumerate(services):

        if ((bool(services[serv].attrs['Spec']['Labels']) == False) or (services[serv].attrs['Spec']['Labels']['com.docker.stack.namespace'] == "iot_app")):
            micro_services.append(services[serv].attrs['Spec']['Name'])

    return micro_services

class ConfigHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Websocket opened")

    def on_message(self, message):
        print(str(message))
        #self.write_message("You said: "+str(message))

    def on_close(self):
        print("Websocket closed")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        client = docker.from_env()
	macro = get_macro(client)
	micro = get_micro(client)

	# Read ini files
        micro_config = read_file("/home/ubuntu/Elascale/conf/microservices.ini")
        macro_config = read_file("/home/ubuntu/Elascale/conf/macroservices.ini")

	# TODO verify if configs list empty. Then apply necessary changes

        self.render("index.html", micro_services=micro, macro_services=macro, micro_config=micro_config, macro_config=macro_config)

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
    #tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port) # This is for the final version
    #http_server.listen(options.port,"172.20.135.51")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    #app = make_app()
    #app.listen(8888)
    #tornado.ioloop.IOLoop.current().start()
    main()
