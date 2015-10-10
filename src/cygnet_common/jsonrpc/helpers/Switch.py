from cygnet_common.jsonrpc.OpenvSwitchTables import OpenvSwitchTable

class OVSwitch(object):

    def __init__(self, bridges=None):
        self.columns = dict()
        for column in OpenvSwitchTable.columns[1:]:
            setattr(self, column, None)

    @classmethod
    def parse(cls, state, uuid, switch_dict):
        assert type(uuid) in [unicode,str]
        assert type(switch_dict) is dict
        assert len(switch_dict) > 0
        switch = cls()
        switch.uuid = uuid
        switch.bridges = dict()
        for row_state, columns in switch_dict.iteritems():
            if row_state == 'new':
                for column, value in columns.iteritems():
                    if column == 'bridges':
                        bridges = []
                        [bridges.extend(val) for val in value[1]]
                        bridges = [bridge for bridge in bridges if bridge != 'uuid']
                    else:
                        state[column] = value
                        switch.columns[column] = value
        for bridge in bridges:
            try:
                switch.bridges[bridge] = state.bridges[bridge]
            except KeyError as e:
                state.bridges[bridge] = None
                switch.bridges[bridge] = None
        return switch

    def addBridge(self, bridge):
        self.columns['bridges'][bridge.uuid] = bridge
    @property
    def bridges(self):
        return self.columns['bridges']

    @bridges.setter
    def bridges(self, value):
        if type(value) is dict:
            self.columns['bridges'] = value
        elif type(value) is list:
            for bridge in value:
                self.columns['bridges'][bridge.uuid] = bridge
        elif not value:
            self.columns['bridges'] = dict()
        else:
            raise TypeError("Switch bridges must be a list of a dictionary")
