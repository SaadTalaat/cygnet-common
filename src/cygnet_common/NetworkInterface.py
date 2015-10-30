from cygnet_common import interfaces
from cygnet_common.Structures import CallbackList


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
        kwargs['endpoints'] = CallbackList(kwargs['endpoints'])
        kwargs['containers'] = CallbackList(kwargs['containers'])
        self['endpoints'] = kwargs['endpoints']
        self['containers'] = kwargs['containers']
        self['interfaces'] = kwargs['interfaces']
        self.network = (getattr(interfaces, kwargs['interface_class']))(self, **kwargs)

        self.endpoints.addCallback(list.append, self.addEndpoint)
        self.endpoints.addCallback(list.remove, self.removeEndpoint)
        self.endpoints.addCallback(list.pop, self.removeEndpoint)

        self.containers.addCallback(list.append, self.connectContainer)
        self.containers.addCallback(list.remove, self.disconnectContainer)
        self.containers.addCallback(list.pop, self.disconnectContainer)

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
        return self.network.initalize()

    def initContainerNetwork(self):
        return self.network.initContainerNetwork()

    # Functionality oriented methods #####
    def addEndpoint(self, *endpoints):
        for endpoint in endpoints:
            if endpoint in self.endpoints:
                print("NetworkInterface: Communication with remote endpoint already established")
                endpoints.remove(endpoint)
        self.network.addEndpoint(*endpoints)

    def removeEndpoint(self, *endpoints):
        for endpoint in endpoints:
            if isinstance(endpoint, int) and (len(self.endpoints) < endpoint or endpoint < 0):
                endpoints.pop(endpoint)
            elif not isinstance(endpoint, int) and self.endpoints.index(endpoint) < 0:
                print("NetworkInterface: Cannot remove non-existent endpoint")
                endpoints.remove(endpoint)
        self.network.removeEndpoint(*endpoints)

    def connectContainer(self, *containers):
        for container in containers:
            if container in self.containers:
                print("NetworkInterface: Container already connected")
                containers.remove(container)
        self.network.connectContainer(*containers)

    def disconnectContainer(self, *containers):
        for container in containers:
            if isinstance(container, int) and (len(self.containers) < container or container < 0):
                print("NetworkInterface: Cannot disconnect container, container isn't connected in the first place")
                containers.pop(container)
            elif not isinstance(container, int) and self.containers.index(container) < 0:
                print("NetworkInterface: Cannot disconnect container, container isn't connected in the first place")
                containers.remove(container)
        self.network.disconnectContainer(*containers)
