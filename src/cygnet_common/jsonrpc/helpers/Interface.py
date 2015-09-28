
class OVSInterface(object):


    def __init__(self, state, uuid, interface_dict):
        assert type(interface_dict) is dict
        assert len(interface_dict) > 0
        assert type(uuid) in [str,unicode]
        self.uuid = uuid
        for state, columns in interface_dict.iteritems():
            #XXX: Handle old states
            if state == 'new':
                for column, value in columns.iteritems():
                    if type(value) in [list,tuple] and value[0] == 'set':
                        setattr(self,column, value[1])
                    else:
                        setattr(self, column, value)
        return
