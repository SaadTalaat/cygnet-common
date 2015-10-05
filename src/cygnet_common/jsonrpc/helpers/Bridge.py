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

        for row_state, columns in bridge_dict.iteritems():
            if row_state == 'new':
                for column, value in columns.iteritems():
                    if column == 'ports' and value[0] == 'set':
                        ports = []
                        [ports.extend(val) for val in value[1]]
                        ports = [port for port in ports if port != 'uuid']
                    elif column == 'ports':
                        ports = [p for p in value if p != 'uuid']
                    elif type(value) in [tuple, list] and value[0] == 'set':
                        setattr(bridge, column, value[1])
                    else:
                        setattr(bridge, column, value)
        print '------------'
        print ports
        print '------------'
        for port in ports:
            try:
                bridge.ports[port] = state.ports[port]
            except KeyError as e:
                state.ports[port] = None
                bridge.ports[port] = None
        return bridge

