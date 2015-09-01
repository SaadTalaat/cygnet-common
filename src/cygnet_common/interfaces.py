
from pyroute import IPDB
from sarge import run

class OVSInterface(object):
    '''
        Use an OVS client to query the database for current ovs network.
    '''
    def __init__(self):
        self.addr = None
        self.endpoints = []
        self.range_buckets = {}
        for i in range(1,255):
            self.range_buckets[i] = None

        ####
        # Should read database here
        ####

    def initalize(self):
        ip = IPDB()
        try:
            self.addr = list(ip.interfaces['eth1']['ipaddr'])[0]
            self.addr = self.addr[0], str(self.addr[1])
        except Exception as e:
            print e
        finally:
            ip.release()

        self.range_buckets[int(self.addr[0].split(".")[-1])] = 1

    def addEndpoint(self, endpoint):
        run("./cmds/establish-gre.sh" + str(endpoint[1]) + " " + endpoint[2])

    def removeEndpoint(self, endpoint):
        run("ovs-vsctl del-port gre"+str(endpoint[1]))

    def connectContainer(self, container):
        addr = str(container["Address"])
        containerId = str(container["Id"])
        addr_idx = int(addr.split("/")[0].split(".")[-1])
        available = (self.range_buckets[addr_idx] == None)
        if available:
            self.range_buckets[addr_idx] = containerId
            run("pipework br2 -i eth1 "+ containerId + " " + addr)
        else:
            print "Error connecting container",containerId+": Address Already taken by container: ",self.range_buckets[addr_idx]

    def disconnectContainer(self, container):
        addr = str(container["Address"])
        addr_idx = int(addr.split("/")[0].split(".")[-1])
        self.range_buckets[addr_idx]= None
