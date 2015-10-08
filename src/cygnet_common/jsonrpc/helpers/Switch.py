from cynget_common.jsonrpc.OpenvSwitchTables import OpenvSwitchTable

class OVSwitch(object):

    def __init__(self):
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
        for bridge in bridges:
            try:
                switch.bridges[bridge] = state.bridges[bridge]
            except KeyError as e:
                state.bridges[bridge] = None
                switch.bridges[bridge] = None
        return switch
