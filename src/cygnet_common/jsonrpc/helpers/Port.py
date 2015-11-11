from cygnet_common.jsonrpc.OpenvSwitchTables import PortTable
from uuid import uuid1


class OVSPort(object):

    def __init__(self, name=None, interfaces=None):
        self.columns = dict()
        for column in PortTable.columns[1:]:
            setattr(self, column, None)
        self.name = name
        if interfaces:
            self.interfaces = interfaces
        self.uuid_name = 'row' + str(uuid1()).replace('-', '_')
        self.uuid = self.uuid_name

    @classmethod
    def parse(cls, state, uuid, port_dict):
        assert type(uuid) in [str, bytes]
        assert isinstance(port_dict, dict)
        assert len(port_dict) > 0
        port = cls()
        port.uuid = uuid
        port.interfaces = dict()

        for row_state, columns in list(port_dict.items()):
            if row_state == 'new':
                for column, value in list(columns.items()):
                    if column == 'interfaces':
                        interfaces = [i for i in value if i != 'uuid']
                    else:
                        setattr(port, column, value)
        for iface in interfaces:
            try:
                port.interfaces[iface] = state.interfaces[iface]
            except KeyError:
                state.interfaces[iface] = None
                port.interfaces[iface] = None
        return port

    @property
    def name(self):
        return self.columns['name']

    @name.setter
    def name(self, value):
        if type(value) in [str, bytes]:
            self.columns['name'] = value
        elif not value:
            self.columns['name'] = ''
        else:
            raise TypeError("Port name must be a string")

    @property
    def interfaces(self):
        return self.columns['interfaces']

    @interfaces.setter
    def interfaces(self, value):
        if isinstance(value, dict):
            self.columns['interfaces'] = value
        elif isinstance(value, list):
            for iface in value:
                self.columns['interfaces'][iface.uuid] = iface
        elif not value:
            self.columns['interfaces'] = dict()
        else:
            raise TypeError("Port interfaces should be a dictionary or a list")

    @property
    def tag(self):
        return self.columns['tag']

    @tag.setter
    def tag(self, value):
        if isinstance(value, list):
            self.columns['tag'] = value
        elif not value:
            self.columns['tag'] = ['set', []]
        else:
            raise TypeError("Port tags must be a list")

    @property
    def trunks(self):
        return self.columns['trunks']

    @trunks.setter
    def trunks(self, value):
        if isinstance(value, list):
            self.columns['trunks'] = value
        elif not value:
            self.columns['trunks'] = ['set', []]
        else:
            raise TypeError("Port trunks must be a list")
