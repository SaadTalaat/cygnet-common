class OVSBridge(object):

    def __init__(self):
        pass

    @classmethod
    def parse(cls, state, uuid, bridge_dict):
        assert type(uuid) in [str, unicode]
        assert type(bridge_dict) is dict
        assert len(bridge_dict) > 0
        bridge = cls()

        bridge.uuid = uuid
        bridge.ports = dict()

        for state, columns in bridge_dict.iteritems():
            if state == 'new':
                for column, value in columns.iteritems():
                    if column == 'ports':
                        ports = [p for p in value if p != 'uuid']
                    elif type(value) in [tuple, list] and value[0] == 'set':
                        setattr(bridge, column, value[1])
                    else:
                        setattr(bridge, column, value)
        for port in ports:
            bridge.ports[port] = state.ports[port]
        return bridge

