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
        req_enum    = Enum('requests','Open_vSwitch Bridge Port Interface')
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
            bridge = None
            port = None
            for br, dic in self.bridges.iteritems():
                for prt, dic_prt in br['ports'].iteritems():
                    if dic_prt['interfaces'].has_key(uuid):
                        bridge = br
                        port = prt
                        break

            for state, columns in table_states.iteritems():
                if state == 'new':
                    for column, value in columns.iteritems():
                        if type(value) in [list,tuple] and value[0] == 'set':
                            self.bridges[bridge]['ports'][port]['interfaces'][uuid][column] = value[1]
                        else:
                            self.bridge[bridge]['ports'][port]['interfaces'][uuid][column] = value

    def __update_Port(self, result):
        for uuid, table_states in result.iteritems():
            bridge = None
            for br, dic in self.bridges.iteritems():
                if dic['ports'].has_key(uuid):
                    bridge = br
                    break
            for state, columns in table_states.iteritems():
                if state == 'new':
                    for column, value in columns.iteritems():
                        if column == 'interfaces':
                            interfaces = filter(lambda x: x != 'uuid', value)
                            self.__verify_interfaces(bridge,uuid,interfaces)
                        elif type(value) in [list,tuple] and value[0] == 'set':
                            self.bridges[bridge]['ports'][uuid][column] = value[1]
                        else:
                            self.bridges[bridge]['ports'][uuid][column] = value

    def __update_Bridge(self, result):
        for uuid, table_states in result.iteritems():
            ## Is it a new bridge?
            if not self.bridges.has_key(uuid):
                self.bridges[uuid] = BaseDict()
            for state, columns in table_states.iteritems():
                if state == 'new':
                    for column, value in columns.iteritems():
                        if column == 'ports':
                            ports = filter(lambda x: x!='uuid',value)
                            self.__verify_ports(uuid, ports)
                        elif type(value) in [list,tuple] and value[0] == 'set':
                            self.bridges[uuid][column] = value[1]
                        else:
                            self.bridges[uuid][column] = value


    def __update_OpenvSwitch(self, result):
        for uuid, table_states in result.iteritems():
            self['uuid'] = uuid
            for state, columns in table_states.iteritems():
                if state == 'new':
                    for column, value in columns.iteritems():
                        if column == 'bridges':
                            bridges = []
                            [bridges.extend(val) for val in value[1]]
                            bridges = filter(lambda x: x!='uuid',bridges)
                            self.__verify_bridges(bridges)
                        elif type(value) in [list,tuple] and value[0] == 'set':
                            self[column] = value[1]
                        else:
                            self[column] = value


    def __verify_interfaces(self, bridge, port, interface_uuids):
        if not self.bridges[bridge]["ports"][port].has_key("interfaces"):
            self.bridges[bridge]["ports"][port]["interfaces"] = BaseDict()
        exists  = set(self.bridges[bridge]["ports"][port]["interfaces"].keys())
        check   = set(interface_uuids)
        new     = exists ^ check
        for interface_uuid in new:
            self.bridges[bridge]['ports'][port]["interfaces"][interface_uuid] = BaseDict()

    def __verify_ports(self, bridge, port_uuids):
        if not self.bridges[bridge].has_key("ports"):
            self.bridges[bridge]["ports"] = BaseDict()

        exists  = set(self.bridges[bridge]["ports"].keys())
        check   = set(port_uuids)
        new     = exists ^ check
        for port_uuid in new:
            self.bridges[bridge]['ports'][port_uuid] = BaseDict()


    def __verify_bridges(self, bridge_uuids):
        exists  = set(self['bridges'].keys())
        check   = set(bridges_uuids)
        new     = exists ^ check
        for bridge_uuid in new:
            self['bridges'][bridge_uuid] = BaseDict()
