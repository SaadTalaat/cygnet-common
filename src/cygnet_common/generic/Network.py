from cygnet_common.Structures import BaseDict
from cygnet_common.strtypes import unicode

class Network(BaseDict):
    '''
    Network class should be able to
    - initialize its buckets depending on the subnet
    - provide available addresses
    - maintain a list of containers and endpoints attached to it
    '''

    def __init__(self, Id, **config):
        if type(Id) not in [str, bytes, unicode]:
            raise TypeError("Identification must be a string")
        if type(Id)  is bytes and bytes is not str:
            Id = Id.decode('utf-8')
        elif type(Id) is unicode and unicode is not str:
            Id = Id.encode('utf-8')
        self['Id'] = Id
        self['Name'] = None
        self['Address'] = None
        self['Config'] = None
        self.valid = False
        self.bucket = {}
        self.containers = []
        self.mask = 32
        if config:
            self.configure(**config)

    def addrToKey(self, addr):
        key = [int(octet) for octet in \
                addr.split("/")[0].split(".")[\
                len(self.pre_octets):]]
        return tuple(key)

    def configure(self, **config):
        if self.valid:
            return
        pool = config['Pool']
        addr, mask = pool.split("/")
        mask = int(mask)
        self.mask = mask
        self.available = (0xffffffff >> mask)
        pre_octets = [int(octet) for octet in addr.split(".")[:mask/8]]
        self.pre_octets = tuple(pre_octets)
        '''
        # Just in case
        for i in range(0, self.available):
            key = [0]*(4 - len(pre_octets))
            octet = 0xff
            idx = len(key) -1
            while i != 0:
                key[idx] = i & 0xff
                i >>= 8
                idx -= 1
            self.bucket[tuple(key)] = None
        '''
        self['Address'] = config['Gateway'].split("/")[0]
        # Cross out gateway
        addr_key = self.addrToKey(self.Address)
        self.bucket[addr_key] = self
        self['Config'] = config
        self.valid = True

    def attachContainer(self, container):
       addr_key = self.addrToKey(container.address)
       if self.bucket[addr_key]:
           raise RuntimeError("error: Address already taken")
       self.bucket[addr_key] = container
       self.containers.append(container.id)
       container.attachToInterface(self)

    def detachContainer(self, container):
        if container.id not in self.containers:
            raise KeyError("No such container")
        addr_key = self.addrToKey(container.address)
        self.bucket[addr_key] = None
        self.containers.remove(container.id)
        container.detachFromInterface(self)

    def isAttached(self, container):
        return container.id in self.containers

    @property
    def name(self):
        return self.Name

    @name.setter
    def name(self, value):
        if type(value) not in [str, bytes, unicode]:
            raise TypeError("error: network name must be a string")
        if type(value)  is bytes and bytes is not str:
            value = value.decode('utf-8')
        elif type(value) is unicode and unicode is not str:
            value = value.encode('utf-8')
        self['Name'] = value

    @property
    def address(self):
        return self.Address

    @address.setter
    def address(self, value):
        if type(value) not in [str, bytes, unicode]:
            raise TypeError("error: network address must be a string")
        if type(value)  is bytes and bytes is not str:
            value = value.decode('utf-8')
        elif type(value) is unicode and unicode is not str:
            value = value.encode('utf-8')
        addr = value
        mask = self.mask
        if '/' in value:
            addr, mask = value.split("/")
            mask = int(mask)
        self['Address'] = addr
        self.mask = mask

    @property
    def id(self):
        return self.Id

    @id.setter
    def id(self, value):
        if type(value) not in [str, bytes, unicode]:
            raise TypeError("error: network id must be a string")
        if type(value)  is bytes and bytes is not str:
            value = value.decode('utf-8')
        elif type(value) is unicode and unicode is not str:
            value = value.encode('utf-8')
        self['Id'] = value
