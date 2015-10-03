
class OVSPort(object):

    def __init__(self):
        pass

    def parse(cls, state, uuid, port_dict):
        assert type(uuid) in [str, unicode]
        assert type(port_dict) is dict
        assert len(port_dict) > 0
        port = cls()
        port.uuid = uuid
        port.interfaces = dict()

        for state, columns in port_dict.iteritems():
            if state == 'new':
                for column, value in columns.iteritems():
                    if column == 'interfaces':
                        interfaces = [i for i in value if i != 'uuid']
                    elif type(value) in [list,tuple] and value[0] == 'set':
                        setattr(port, column, value[1])
                    else:
                        setattr(port, column, value)
        for iface in interfaces:
            port.interfaces[iface] = state.interfaces[iface]

        return port
