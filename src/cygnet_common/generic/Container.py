from cygnet_common.Structures import BaseDict
from cygnet_common.strtypes import unicode

class Container(BaseDict):
    def __init__(self, Id, node):
        if type(Id) not in [str, unicode, bytes]:
            raise TypeError("Container Id must be a string")
        if type(Id) is bytes and bytes is not str:
            Id = Id.decode('utf-8')
        elif type(Id) is unicode and unicode is not str:
            Id = Id.encode('utf-8')
        self["Id"] = Id
        self["Node"] = node
        self["State"] = 0
        self["Address"] = None
        self["Interface"] = []
        self["Name"] = None

    def attachToInterface(self, iface):
        self["Interface"] = iface
        return self.Interface

    def detachFromInterface(self, iface):
        self["Interface"] = None

    def running(self, flag):
        if flag:
            self['State'] = 1
        else:
            self['State'] = 0
        return self.State

    @property
    def isRunning(self):
        return self.State == 1

    @property
    def hasAddress(self):
        return self.Address is not None

    @property
    def node(self):
        return self.Node

    @property
    def id(self):
        return self.Id

    @property
    def address(self):
        return self.Address

    @address.setter
    def address(self, value):
        if type(value) not in [str, unicode, bytes]:
            raise TypeError("Container Address must be a string")
        if type(value) is bytes and bytes is not str:
            value = value.decode('utf-8')
        elif type(value) is unicode and unicode is not str:
            value = value.encode('utf-8')
        self['Address'] = value

    @property
    def name(self):
        return self.Name

    @name.setter
    def name(self, value):
        if type(value) not in [str, unicode, bytes]:
            raise TypeError("Container Name must be a string")
        if type(value) is bytes and bytes is not str:
            value = value.decode('utf-8')
        elif type(value) is unicode and unicode is not str:
            value = value.encode('utf-8')
        if type(value) is not str:
            raise TypeError("error: container name must be a string")
        self['Name'] = value
