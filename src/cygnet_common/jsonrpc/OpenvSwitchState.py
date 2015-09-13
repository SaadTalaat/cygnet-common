from cygnet_common.jsonrpc.OpenvSwitchTables import *


class BaseDict(dict):
    def __getattribute__(self, key, *args):
        try:
            return dict.__getattribute__(self, key)
        except AttributeError as e:
            if key in self:
                return self[key]
            else:
                raise e

    def __setattr__(self, key, value):
        try:
            dict.__setattr__(self, key, value)
        except AttributeError as e:
            if key in self:
                self[key] = value
            else:
                raise e
    def __delattr__(self, key):
        try:
            dict.__delattr__(self, key)
        except AttributeError as e:
            if key in self:
                del self[key]
            else:
                raise e

class OpenvSwitchState(BaseDict):
    '''
    Initially, OpenvSwitchState should include the current OVS
    bridges with their corresponding ports,interfaces and controllers

    OpenvSwitchState is directly updated from JSONRPC responses
    to JSONRPC methods
    XXX: Needs extension
    '''

    def __init__(self,**kwargs):
        if kwargs:
            # Copy another state
            # XXX: Validate given state
            dict.__init__(self, **kwargs)
        else:
            # Make empty state
            self['bridges']     = []
            self['ovs_version'] = None
            self['cur_cfg']     = None
            self['uuid']        = None

    def update(self, requests, response):
        result = response['result']
        for request in requests:
            table = request.__name__
            if not result.has_key(table):
                continue
            if table == OpenvSwitchTable.__name__:
                self.__update_OpenvSwitch(result[table])

    def __update_OpenvSwitch(self, result):
        for uuid, table_states in request.iteritems():
            self['uuid'] = uuid
            for state, columns in table_states.iteritems():
                if state == 'new':
                    for column, value in columns.iteritems():
                        if column == 'bridges':
                            bridges = []
                            [bridges.extend(val) for val in value[1]]
                            bridges = filter(lambda x: x!='uuid',bridges)
                            self.__verify_bridges(bridges)
                        if type(value) in [list,tuple] and value[0] == 'set':
                            self[column] = value[1]

    def __verify_bridges(self,bridge_uuids):
        exists  = set(self['bridges'].keys())
        check   = set(bridges_uuids)
        new     = exists ^ check
        for bridge_uuid in new:
            self['bridges'][bridge] = dict()
