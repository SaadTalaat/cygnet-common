import interfaces
class NetworkInterface(dict):

    '''
    Network components should be defined the following sets:
        - Endpoints
        - Containers
        - Interfaces

    Network Types:
    - OpenvSwitch


    TODO:
        mirror components managed by the cygnet_common to
        the etcd server. For which we'll need to code another etcd client
        :
    '''
    def __init__(self, **kwargs):
        self['endpoints'] = kwargs['endpoints']
        self['containers'] = kwargs['containers']
        self['interfaces'] = kwargs['interfaces']
        self.network = (getattr(interfaces, kwargs['interface_class']))(self, **kwargs)

    def __getattribute__(self, key, *args):
        try:
            print key
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
        return self.network.initalize()

    def initContainerNetwork(self, count):
        return self.network.initContainerNetwork(count)

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
