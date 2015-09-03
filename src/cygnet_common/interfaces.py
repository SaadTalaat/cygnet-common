
from pyroute2 import IPRoute, IPDB
from sarge import run

class OVSInterface(dict):
    '''
        Use an OVS client to query the database for current ovs network.
    '''
    def __init__(self, interface, **kwargs):
        dict.__init__(self,kwargs)
        self.addr = None
        self.range_buckets = {}
        self.interface = interface
        for i in range(1,255):
            self.range_buckets[i] = None
        self['endpoints'] = kwargs['endpoints']
        self['containers'] = kwargs['containers']
        self['interfaces'] = kwargs['interfaces']
        ####
        # Should read database here
        ####

    def __getattribute__(self, key, *args):
        try:
            return dict.__getattribute__(self, key)
        except AttributeError as e:
            if key in self:
                return self[key]
            else:
                raise e

    def __setattr__(self, key, value):
        try:
            dict.__setattr__(self, key, value)
        except AttributeError as e:
            if key in self:
                self[key] = value
            else:
                raise e
    def __delattr__(self, key):
        try:
            dict.__delattr__(self, key)
        except AttributeError as e:
            if key in self:
                del self[key]
            else:
                raise e

    def initalize(self):
        ip = IPDB()
        try:
            ## Check if public interface is up
            self.addr = list(ip.interfaces['br1']['ipaddr'])[0]
            self.addr = self.addr[0], str(self.addr[1])
            self.interface.interfaces.append(('br1',self.addr))
            self.interfaces.append(('br1',self.addr))
        except Exception as e:
            print e
        finally:
            ip.release()

        self.range_buckets[int(self.addr[0].split(".")[-1])] = 1
        return addr

    def initContainerNetwork(self, count):
        ip = IPRoute()
        mask = 16
        addr = "10.1."+str(count)+".1"
        run("ifconfig br2 "+addr2)
        ip.addr('add',
                index=(ip.link_lookup(ifname='br2')),
                address='addr',
                mask=mask)
        self.interface.interfaces.append(('br2',(self.addr,mask)))
        self.interfaces.append(('br2',(self.addr,str(mask))))
        return addr

    def addEndpoint(self, endpoint):
        run("./cmds/establish-gre.sh" + str(endpoint[1]) + " " + endpoint[2])
        self.endpoints.append(endpoint)

    def removeEndpoint(self, endpoint):
        run("ovs-vsctl del-port gre"+str(endpoint[1]))
        del self.endpoints[self.endpoints.index(endpoint)]

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
        self.containers.append(container)

    def disconnectContainer(self, container):
        addr = str(container["Address"])
        addr_idx = int(addr.split("/")[0].split(".")[-1])
        self.range_buckets[addr_idx]= None
        del self.containers[self.containers.index(container)]
