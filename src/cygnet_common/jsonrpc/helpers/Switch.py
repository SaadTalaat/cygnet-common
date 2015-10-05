
class OVSwitch(object):

    def __init__(self):
        pass

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
                    elif type(value) in [list, tuple] and value[0] == 'set':
                        state[column] = value[1]
                    else:
                        state[column] = value
        print state
        for bridge in bridges:
            try:
                switch.bridges[bridge] = state.bridges[bridge]
            except KeyError as e:
                state.bridges[bridge] = None
                switch.bridges[bridge] = None
        return switch
