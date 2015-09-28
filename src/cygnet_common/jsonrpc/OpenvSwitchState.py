from cygnet_common.jsonrpc.OpenvSwitchTables import *
from cygnet_common.jsonrpc.helpers.Port import OVSPort
from cygnet_common.jsonrpc.helpers.Interface import OVSInterface
from cygnet_common.jsonrpc.helpers.Bridge import OVSBridge

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

    Example layout
    state = {
            "ovs_version"   :"2.1.1",
            "cur_cfg"       :202,
            "bridges"       :{
                "uuid-bridge-1":{
                    "name"  :"foo",
                    "ports" :{
                        "uuid-port-1":{
                            "name"      :"foo-port",
                            "type"      :"internal",
                            "interfaces":{
                                "name":"foo-interface"
                            }
                        }
                    }
                },
                "uuid-bridge-2":{
                }
            }


    }
    '''

    def __init__(self,**kwargs):
        if kwargs:
            # Copy another state
            # XXX: Validate given state
            dict.__init__(self, **kwargs)
        else:
            # Make empty state
            self['bridges']     = BaseDict()
            self['ports']       = BaseDict()
            self['interfaces']  = BaseDict()
            self['ovs_version'] = None
            self['cur_cfg']     = None
            self['uuid']        = None

    def update(self, requests, response):
        result = response['result']
        requests = self.__sort_Requests(requests)
        for request in requests:
            table = request.__name__
            if not result.has_key(table):
                continue
            if table == OpenvSwitchTable.__name__:
                self.__update_OpenvSwitch(result[table])
            elif table == BridgeTable.__name__:
                self.__update_Bridge(result[table])
            elif table == PortTable.__name__:
                self.__update_Port(result[table])
            elif table == InterfaceTable.__name__:
                self.__update_Interface(result[table])

    def __sort_Requests(self, requests):
        from enum import Enum
        req_enum    = Enum('requests','Interface Port Bridge Open_vSwitch')
        result      = [None]*len(requests)
        for i in range(0,len(result)):
            r   = requests[i]
            idx = req_enum[r.__name__].value
            result[idx] = r
            requests.remove(r)
        result = filter(lambda x: x, result)
        result.extend(requests)
        return result


    def __update_Interface(self, result):
        for uuid, table_states in result.iteritems():
            self.interface[uuid] = OVSInterface(self, uuid, table_states)

    def __update_Port(self, result):
        for uuid, table_states in result.iteritems():
            self.ports[uuid] = OVSPort(self, uuid, table_states)

    def __update_Bridge(self, result):
        for uuid, table_states in result.iteritems():
            self.bridges[uuid] = OVSBridge(self, uuid, table_states)

    def __update_OpenvSwitch(self, result):
        for uuid, table_states in result.iteritems():
            self['uuid'] = uuid
            self.switch = OVSwitch(self, uuid, table_states)

