from cygnet_common.jsonrpc.OpenvSwitchTables import OpenvSwitchTable


class OVSwitch(object):

    def __init__(self, state, bridges=None):
        self.columns = dict()
        for column in OpenvSwitchTable.columns[1:]:
            setattr(self, column, None)
        self.state = state

    @classmethod
    def parse(cls, state, uuid, switch_dict):
        assert type(uuid) in [unicode, str]
        assert type(switch_dict) is dict
        assert len(switch_dict) > 0
        switch = cls(state)
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
            except KeyError:
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

    @property
    def cur_cfg(self):
        return self.columns['cur_cfg']

    @cur_cfg.setter
    def cur_cfg(self, value):
        if type(value) is int:
            self.columns['cur_cfg'] = value
        elif not value:
            self.columns['cur_cfg'] = 0
        else:
            raise TypeError("value must be an integer")

    @property
    def next_cfg(self):
        return self.columns['next_cfg']

    @next_cfg.setter
    def next_cfg(self, value):
        if type(value) is int:
            self.columns['next_cfg'] = value
        elif not value:
            self.columns['next_cfg'] = 0
        else:
            raise TypeError("value must be an integer")

    @property
    def manager_options(self):
        return self.columns['manager_options']

    @manager_options.setter
    def manager_options(self, value):
        if type(value) is list:
            self.columns['manager_options'] = value
        elif not value:
            self.columns['manager_options'] = ['set', []]
        else:
            raise TypeError("value must be an integer")
