from cygnet_common.jsonrpc.OpenvSwitchTables import InterfaceTable
from cygnet_common.jsonrpc.OVSTypes import OVSMap
from uuid import uuid1


class OVSInterface(object):

    def __init__(self, name=None, interface_type=None):
        self.columns = dict()
        for column in InterfaceTable.columns[1:]:
            setattr(self, column, None)
        self.name = name
        if interface_type:
            self.type = interface_type
        self.uuid_name = 'row' + str(uuid1()).replace('-', '_')
        self.uuid = self.uuid_name

    @classmethod
    def parse(cls, state, uuid, interface_dict):
        assert isinstance(interface_dict, dict)
        assert len(interface_dict) > 0
        assert type(uuid) in [str, bytes]
        interface = cls()
        interface.uuid = uuid
        for row_state, columns in list(interface_dict.items()):
            # XXX: Handle old states
            if row_state == 'new':
                for column, value in list(columns.items()):
                    setattr(interface, column, value)
        return interface

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
            raise TypeError("value must be a string")

    @property
    def type(self):
        return self.columns['type']

    @type.setter
    def type(self, value):
        if type(value) in [str, bytes]:
            self.columns['type'] = value
        elif not value:
            self.columns['type'] = ''
        else:
            raise TypeError("value must be a string")

    @property
    def options(self):
        return self.columns['options']

    @options.setter
    def options(self, value):
        if isinstance(value, list):
            self.columns['options'] = OVSMap(value)
        elif not value:
            self.columns['options'] = OVSMap()
        else:
            print((type(value)))
            raise TypeError("value must be a list")

    @property
    def mac(self):
        return self.columns['mac']

    @mac.setter
    def mac(self, value):
        if isinstance(value, list):
            self.columns['mac'] = value
        elif not value:
            self.columns['mac'] = ['set', []]
        else:
            raise TypeError("value must be a list")
