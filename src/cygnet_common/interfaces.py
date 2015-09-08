
from pyroute2 import IPRoute, IPDB
from sarge import run
from cygnet_common.Structures import CallbackList

def __getIPv4Addr__(addr_list):
    '''
    return first ip4 addr it hits
    '''
    assert isinstance(addr_list,list)
    for addr in addr_list:
        try:
            assert (len(addr[0].split(".")) == 4)
            return addr
        except:
            continue
    return None

class OVSInterface(dict):
    '''
        Use an OVS client to query the database for current ovs network.
    '''
    def __init__(self, interface, **kwargs):
        self.addr = None
        self.range_buckets = {}
        self.interface = interface
        for i in range(1,255):
            self.range_buckets[i] = None
        self['endpoints'] = kwargs['endpoints']
        self['containers'] = kwargs['containers']
        self['interfaces'] = kwargs['interfaces']

        ## Add callbacks
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
            self.addr = __getIPv4Addr__(list(ip.interfaces.br1.ipaddr))
            print list(ip.interfaces['br1']['ipaddr'])
            self.addr = self.addr[0], str(self.addr[1])
            #self.interface.interfaces.append(('br1',self.addr))
            self.interfaces.append(('br1',self.addr))
        except Exception as e:
            print e
        finally:
            ip.release()
        self.range_buckets[int(self.addr[0].split(".")[-1])] = 1
        return self.addr

    def initContainerNetwork(self, count):
        ip = IPRoute()
        mask = 16
        addr = "10.1."+str(count)+".1"
        #run("ifconfig br2 "+addr2)
        ip.addr('add',
                index=(ip.link_lookup(ifname='br2')),
                address=addr,
                mask=mask)
        self.interfaces.append(('br2',(self.addr,str(mask))))
        return addr

    def addEndpoint(self, *endpoints):
        for endpoint in endpoints:
            run("ovs-vsctl add-port br2 gre"+str(len(self.endpoints))+  
                    " -- set Interface gre"+str(len(self.endpoints))+" type=gre options:remote_ip="+(endpoint))
            #run("establish-gre.sh" + str(endpoint[1]) + " " + endpoint[2])
            #self.endpoints.append(endpoint)

    def removeEndpoint(self, *endpoints):
        for e in endpoints:
            endpoint = None
            if isinstance(endpoint,int):
              endpoint = self.endpoints[e]
            else:
                endpoint = e
            run("ovs-vsctl del-port gre"+str(endpoints.index(endpoint)))
            #del self.endpoints[self.endpoints.index(endpoint)]

    def connectContainer(self, *containers):
        for container in containers:
            addr = str(container["Address"])
            containerId = str(container["Id"])
            addr_idx = int(addr.split("/")[0].split(".")[-1])
            available = (self.range_buckets[addr_idx] == None)
            if available:
                self.range_buckets[addr_idx] = containerId
                run("pipework br2 -i eth1 "+ containerId + " " + addr)
            else:
                print "Error connecting container",containerId+": Address Already taken by container: ",self.range_buckets[addr_idx]
            #self.containers.append(container)

    def disconnectContainer(self, *containers):
        for c in containers:
            if isinstance(c,int):
                container = self.containers[c]
            else:
                container = c
            addr = str(container["Address"])
            addr_idx = int(addr.split("/")[0].split(".")[-1])
            self.range_buckets[addr_idx]= None
            #del self.containers[self.containers.index(container)]
