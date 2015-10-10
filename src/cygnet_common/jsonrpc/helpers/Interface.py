from cygnet_common.jsonrpc.OpenvSwitchTables import InterfaceTable
from uuid import uuid1

class OVSInterface(object):

    def __init__(self, name=None, interface_type=None):
        self.columns = dict()
        for column in InterfaceTable.columns[1:]:
            setattr(self, column, None)
        self.name = name
        if interface_type:
            self.type = interface_type
        self.uuid_name = 'row' + str(uuid1()).replace('-','_')
        self.uuid = self.uuid_name

    @classmethod
    def parse(cls, state, uuid, interface_dict):
        assert type(interface_dict) is dict
        assert len(interface_dict) > 0
        assert type(uuid) in [str,unicode]
        interface = cls()
        interface.uuid = uuid
        for row_state, columns in interface_dict.iteritems():
            #XXX: Handle old states
            if row_state == 'new':
                for column, value in columns.iteritems():
                    setattr(interface, column, value)
        return interface

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
            raise TypeError("Interface name must be a string")

    @property
    def type(self):
        return self.columns['type']

    @type.setter
    def type(self, value):
        if type(value) in [str, unicode]:
            self.columns['type'] = value
        elif not value:
            self.columns['type'] = ''
        else:
            raise TypeError("Interface type must be a string")

    @property
    def options(self):
        return self.columns['options']

    @options.setter
    def options(self, value):
        if type(value) is list:
            self.columns['options'] = value
        elif not value:
            self.columns['options']= ['map',[]]
        else:
            raise TypeError("Interface options must be a list")
