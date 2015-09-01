
from interfaces import OVSInterface
from MutantDict import MutantDictBase

class NetworkInterface(MutantDictBase):

    '''
    Network components should be defined the following sets:
        - Endpoints
        - Containers
        - Interfaces

    Network Types:
    - OpenvSwitch

    '''
    ## Types
    OVS = 0

    def __init__(self, interface_type):
        super(NetworkInterface, self).__init__()
        self.network = {0: OVSInterface,
                99: None}.get(interface_type, 99)()
        self.network.initialize()
        self['endpoints'] = []
        self['containers'] = []
        self['interfaces'] = []

    ##### Functionality oriented methods #####
    def addEndpoint(self, endpoint):
        if self.endpoints.index[endpoint] >= 0:
            print "NetworkInterface: Communication with remote endpoint already established"
            return
        self.endpoints.append(endpoint)
        self.network.addEndpoint(endpoint)

    def removeEndpoint(self, endpoint):
        if self.endpoints.index[endpoint] < 0:
            print "NetworkInterface: Cannot remove non-existent endpoint"
            return
        self.network.removeEndpoint(endpoint)
        del self.endpoints[self.endpoints.index(endpoint)]


    def connectContainer(self, container):
        if self.containers.index[container] >= 0:
            print "NetworkInterface: Container already connected"
            return
        self.containers.append(container)
        self.network.connectContainer(container)

    def disconnectContainer(self, container):
        if self.containers.index[container] < 0:
            print "NetworkInterface: Cannot disconnect container, container isn't connected in the first place"
            return
        del self.containers[self.containers.index(container)]

    ##### Type oriented methods ######
    def __keytransform__(self, key):
        key = key.lower()
        if key.find("interfaces") >=0 or key.find("endpoints") >= 0 or key.find("containers") >= 0:
            return key
        else:
            raise NameError("NetworkInterface: Illegal key")

    @property
    def interfaces(self):
        return self['interfaces']

    @property
    def endpoints(self):
        return self['endpoints']

    @property
    def containers(self):
        return self['containers']
