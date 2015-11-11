from pyroute2 import IPRoute, IPDB
from sarge import run


def __getIPv4Addr__(addr_list):
    '''
    return first ip4 addr it hits
    '''
    assert isinstance(addr_list, list)
    for addr in addr_list:
        try:
            assert (len(addr[0].split(".")) == 4)
            return addr
        except:
            continue
    return None


class openvswitch(dict):
    '''
        Use an OVS client to query the database for current ovs network.
    '''
    def __init__(self, interface, **kwargs):
        self.addr = None
        self.range_buckets = {}
        self.tunnel_bucket = {}
        self.interface = interface
        for i in range(1, 255):
            self.tunnel_bucket[i] = None
            self.range_buckets[i] = None
        self['endpoints'] = kwargs['endpoints']
        self['containers'] = kwargs['containers']
        self['interfaces'] = kwargs['interfaces']
        self['internal_ip'] = kwargs['internal_ip']
        # Add callbacks
        #
        # Should read database here
        #

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
            # Check if public interface is up
            self.addr = __getIPv4Addr__(list(ip.interfaces.br1.ipaddr))
            self.addr = self.addr[0], str(self.addr[1])
            self.interfaces.append(('br1', self.addr))
        except Exception as e:
            print(e)
        finally:
            ip.release()
        self.range_buckets[int(self.addr[0].split(".")[-1])] = 1
        return self.addr

    def initContainerNetwork(self):
        ip = IPRoute()
        try:
            addr = self['internal_ip'].split('/')[0]
            mask = int(self['internal_ip'].split('/')[1])
        except KeyError as e:
            print("OpenvSwitch: CYGNET_INTERNAL_IP environment variable not found")
            raise e
        ip.addr('add',
                index=(ip.link_lookup(ifname='br2')),
                address=addr,
                mask=mask)
        run("ifconfig br2 up")
        self.interfaces.append(('br2', (self.addr, str(mask))))
        return addr

    def addEndpoint(self, *endpoints):
        for endpoint in endpoints:
            keys = [key for key, value in list(self.tunnel_bucket.items()) if value is None]
            if keys:
                available = keys[0]
                self.tunnel_bucket[available] = endpoint
            else:
                raise IndexError
            run("ovs-vsctl add-port br2 gre" + str(available) +
                " -- set Interface gre" + str(available) + " type=gre options:remote_ip=" + (endpoint))

    def removeEndpoint(self, *endpoints):
        for e in endpoints:
            endpoint = None
            if isinstance(e, int):
                endpoint = self.endpoints[e]
            else:
                endpoint = e
            tunnel_idx = [idx for idx, ep in list(self.tunnel_bucket.items()) if ep == endpoint]
            if tunnel_idx:
                tunnel_idx = tunnel_idx[0]
            else:
                raise ValueError
            run("ovs-vsctl del-port gre"+str(tunnel_idx))
            self.tunnel_bucket[tunnel_idx] = None

    def connectContainer(self, *containers):
        for container in containers:
            addr = str(container["Address"])
            containerId = str(container["Id"])
            addr_idx = int(addr.split("/")[0].split(".")[-1])
            available = (self.range_buckets[addr_idx] is None)
            if available:
                self.range_buckets[addr_idx] = containerId
                run("pipework br2 -i eth1 " + containerId + " " + addr)
            else:
                print(("Error connecting container", containerId + ": Address Already taken by container: ", self.range_buckets[addr_idx]))

    def disconnectContainer(self, *containers):
        for c in containers:
            if isinstance(c, int):
                container = self.containers[c]
            else:
                container = c
            addr = str(container["Address"])
            addr_idx = int(addr.split("/")[0].split(".")[-1])
            self.range_buckets[addr_idx] = None
