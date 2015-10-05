
class OVSPort(object):

    def __init__(self):
        pass
    @classmethod
    def parse(cls, state, uuid, port_dict):
        assert type(uuid) in [str, unicode]
        assert type(port_dict) is dict
        assert len(port_dict) > 0
        port = cls()
        port.uuid = uuid
        port.interfaces = dict()

        for row_state, columns in port_dict.iteritems():
            if row_state == 'new':
                for column, value in columns.iteritems():
                    if column == 'interfaces':
                        interfaces = [i for i in value if i != 'uuid']
                    elif type(value) in [list,tuple] and value[0] == 'set':
                        setattr(port, column, value[1])
                    else:
                        setattr(port, column, value)
        for iface in interfaces:
            try:
                port.interfaces[iface] = state.interfaces[iface]
            except KeyError as e:
                state.interfaces[iface] = None
                port.interfaces[iface]  = None
        return port
