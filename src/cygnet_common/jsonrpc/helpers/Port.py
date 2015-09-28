
class OVSPort(object):


    def __init__(self, state, uuid, port_dict):
        assert type(uuid) in [str, unicode]
        assert type(port_dict) is dict
        assert len(port_dict) > 0

        self.uuid = uuid
        self.interfaces = dict()

        for state, columns in port_dict.iteritems():
            if state == 'new':
                for column, value in columns.iteritems():
                    if column == 'interfaces':
                        interfaces = [i for i in value if i != 'uuid']
                    elif type(value) in [list,tuple] and value[0] = 'set':
                        setattr(self, column, value[1])
                    else:
                        setattr(self, column, value)
        for iface in interfaces:
            self.interfaces[iface] = state.interfaces[iface]

