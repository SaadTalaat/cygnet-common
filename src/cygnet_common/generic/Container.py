from cygnet_commmon.Structures import BaseDict

class Container(BaseDict):
    def __init__(self, Id, node):
        self["Id"] = Id
        self["Node"] = node
        self["State"] = 0
        self["Address"] = None
        self["Interface"] = []

    def attachToInterface(self, iface):
        self["Interface"] = iface
        return self.Interface

    def detachFromInterface(self, iface):
        self["Interface"] = None

    def running(self, flag):
        if flag:
            self.State = 1
        else:
            self.State = 0
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
        if type(value) is not str:
            raise TypeError("error: container address must be a string")
        self.Address = value
