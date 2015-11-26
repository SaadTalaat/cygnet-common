from pyroute2 import IPDB
from sarge import run
from cygnet_common.jsonrpc.OpenvSwitchClient import OpenvSwitchClient
from cygnet_common.jsonrpc.OpenvSwitchTables import OpenvSwitchTable, BridgeTable, PortTable, InterfaceTable
from cygnet_common.jsonrpc.OVSTypes import OVSAtom


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
        self['external_iface'] = kwargs['external_iface']
        # Add callbacks
        #
        # Should read database here
        # Initialize database client
        self.ovs_client = OpenvSwitchClient('unix:///var/run/openvswitch/db.sock')
        # Tables we shall operate on
        self.ovs_client.getState([OpenvSwitchTable(),
                                  BridgeTable(),
                                  PortTable(),
                                  InterfaceTable()])

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

    def __ovs_setup(self):
        if not self.ovs_client.bridgeExists('cygnet0'):
            self.ovs_client.addBridge('cygnet0')
            self.ovs_client.addPort('cygnet0', self.external_iface)
        elif not self.ovs_client.portExists(self.external_iface):
            self.ovs_client.addPort('cygnet0', self.external_iface)
        ip = IPDB()
        ifaces = ip.interfaces
        ifaces.cygnet0.begin()
        addrs= ip.interfaces[self.external_iface].ipaddr.raw
        addr = None
        for address, attrs in addrs.items():
            if __getIPv4Addr__([address]) == None:
                continue
            addr = address
        ifaces.cygnet0.add_ip(addr[0], int(addr[1]))
        ifaces.cygnet0.up()
        ifaces.cygnet0.commit()
        ifaces[self.external_iface].begin()
        ifaces[self.external_iface].down()
        ifaces[self.external_iface].commit()

        ifaces[self.external_iface].begin()
        ifaces[self.external_iface].up()
        ifaces[self.external_iface].commit()

        ip.release()

    def initalize(self):
        # check if our setup already exists
        self.__ovs_setup()
        ip = IPDB()
        try:
            # Check if public interface is up
            self.addr = __getIPv4Addr__(list(ip.interfaces.cygnet0.ipaddr))
            self.addr = self.addr[0], str(self.addr[1])
            self.interfaces.append(('cygnet0', self.addr))
        except Exception as e:
            raise e
        finally:
            ip.release()
        self.range_buckets[int(self.addr[0].split(".")[-1])] = 1
        return self.addr

    # initContainerNetwork should support both docker < 1.9.0
    # and docker <= 1.9.0
    # - name and network configurations should only be passed
    #   by docker plugin
    # - Otherwise, we are operating on a single internal network
    #   which is only useed by docker < 1.9.0 powerstrip adapter

    def initContainerNetwork(self, iface_id=None, config=None):
        if not iface_id or not config:
            try:
                iface_name = "cygnet_internal"
                if not self.ovs_client.bridgeExists('cygnet_internal'):
                    self.ovs_client.addBridge('cygnet_internal')
                    self.ovs_client.setBridgeProperty('cygnet_internal',
                                                      'stp_enable',
                                                      True)
                addr = self['internal_ip'].split('/')[0]
                mask = int(self['internal_ip'].split('/')[1])
            except KeyError as e:
                print("OpenvSwitch: CYGNET_INTERNAL_IP \
                        environment variable not found")
                raise e
        else:
            iface_name = "cygnet_" + iface_id[:8]
            if not self.ovs_client.bridgeExists(iface_name):
                self.ovs_client.addBridge(iface_name)
                self.ovs_client.setBridgeProperty(iface_name,
                                                  'stp_enable',
                                                  True)
            addr = config['Gateway'].split('/')[0]
            mask = int(config['Gateway'].split('/')[1])
        ip = IPDB()
        ifaces = ip.interfaces
        ifaces[iface_name].begin()
        ifaces[iface_name].add_ip(addr, mask)
        ifaces[iface_name].up()
        ifaces[iface_name].commit()
        ip.release()
        self.interfaces.append((iface_name, (self.addr, str(mask))))
        return iface_name

    def destroyContainerNetwork(self, name):
        if self.ovs_client.bridgeExists(name):
            self.ovs_client.removeBridge(name)
            match = [iface for iface in self.interfaces if iface[0] == name]
            for entry in match:
                self.interfaces.remove(entry)
            return True
        else:
            return False
    def addEndpoint(self, *endpoints):
        for endpoint in endpoints:
            keys = [key for key, value in list(self.tunnel_bucket.items()) if value is None]
            if keys:
                available = keys[0]
                self.tunnel_bucket[available] = endpoint
            else:
                raise IndexError
            iface_name = 'gre' + str(available)
            self.ovs_client.addPort(iface_name)
            iface = self.ovs_client.getInterface(iface_name)
            iface.options.append(OVSAtom['remote_ip', endpoint])
            iface.type = 'gre'
            self.ovs_client.setInterfaceProperty(iface_name, 'type', iface.type)
            self.ovs_client.setInterfaceProperty(iface_name,
                                                 'options',
                                                 iface.options)
            # run("ovs-vsctl add-port br2 gre" + str(available) +
            # " -- set Interface gre" + str(available) + " type=gre options:remote_ip=" + (endpoint))

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
            iface_name = 'gre' + str(tunnel_idx)
            self.ovs_client.removePort(iface_name)
            # run("ovs-vsctl del-port gre"+str(tunnel_idx))
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
