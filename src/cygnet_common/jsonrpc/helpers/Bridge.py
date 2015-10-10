from cygnet_common.jsonrpc.OpenvSwitchTables import BridgeTable
from uuid import uuid1

class OVSBridge(object):

    def __init__(self,name=None, ports=None):
        self.columns = dict()
        for column in BridgeTable.columns[1:]:
            setattr(self, column, None)
        self.name = name
        if ports:
            self.ports = ports
        self.uuid_name = 'row' + str(uuid1()).replace('-','_')
        self.uuid = self.uuid_name

    @classmethod
    def parse(cls, state, uuid, bridge_dict):
        assert type(uuid) in [str, unicode]
        assert type(bridge_dict) is dict
        assert len(bridge_dict) > 0
        bridge = cls()

        bridge.uuid = uuid
        bridge.ports = dict()

        for row_state, columns in bridge_dict.iteritems():
            if row_state == 'new':
                for column, value in columns.iteritems():
                    if column == 'ports' and value[0] == 'set':
                        ports = []
                        [ports.extend(val) for val in value[1]]
                        ports = [port for port in ports if port != 'uuid']
                    elif column == 'ports':
                        ports = [p for p in value if p != 'uuid']
                    else:
                        setattr(bridge, column, value)
        for port in ports:
            try:
                bridge.ports[port] = state.ports[port]
            except KeyError as e:
                state.ports[port] = None
                bridge.ports[port] = None
        return bridge

    @property
    def name(self):
        return self.columns['name']

    @name.setter
    def name(self, value):
        if type(value) in [str, unicode]:
            self.columns['name'] = value
        elif not value:
            self.columns['name'] = ''
        else:
            raise TypeError("Bridge name must be a string")

    @property
    def ports(self):
        return self.columns['ports']

    @ports.setter
    def ports(self, value):
        if type(value) is dict:
            self.columns['ports'] = value
        elif type(value) is list:
            for iface in value:
                self.columns['ports'][iface.uuid] = iface
        elif not value:
            self.columns['ports'] = dict()
        else:
            raise TypeError("Bridge ports should be a dictionary or a list")
