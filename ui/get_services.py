import docker

def get_macro():

    client = docker.from_env()
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

def get_micro():

    client = docker.from_env()
    nodes = client.nodes.list()

    services = client.services.list()

    micro_services = []

    for serv, val in enumerate(services):

        if ((bool(services[serv].attrs['Spec']['Labels']) == False) or (services[serv].attrs['Spec']['Labels']['com.docker.stack.namespace'] == "iot_app")):
            micro_services.append(services[serv].attrs['Spec']['Name'])

    return micro_services


def main():
    client = docker.from_env()

    nodes = client.nodes.list()

    macro_services = []

    for node, val in enumerate(nodes):

	try:
            loc = nodes[node].attrs['Spec']['Labels']['loc']
        except KeyError:
	    continue # Goes back to the beginning of for loop
	else:
	    macro_services.append(nodes[node].attrs['Description']['Hostname'])

    print macro_services


    services = client.services.list()

    micro_services = []

    for serv, val in enumerate(services):

	if ((bool(services[serv].attrs['Spec']['Labels']) == False) or (services[serv].attrs['Spec']['Labels']['com.docker.stack.namespace'] == "iot_app")):
            micro_services.append(services[serv].attrs['Spec']['Name'])

    print micro_services
 


if __name__=="__main__":
  main()
