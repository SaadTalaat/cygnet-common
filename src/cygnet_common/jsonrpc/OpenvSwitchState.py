from cygnet_common.jsonrpc import OpenvSwitchTables as OVSTables
from cygnet_common.jsonrpc.helpers.Port import OVSPort
from cygnet_common.jsonrpc.helpers.Interface import OVSInterface
from cygnet_common.jsonrpc.helpers.Bridge import OVSBridge
from cygnet_common.jsonrpc.helpers.Switch import OVSwitch
from cygnet_common.Structures import BaseDict


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

    def __init__(self, **kwargs):
        if kwargs:
            # Copy another state
            # XXX: Validate given state
            dict.__init__(self, **kwargs)
        else:
            # Make empty state
            self['bridges'] = BaseDict()
            self['ports'] = BaseDict()
            self['interfaces'] = BaseDict()
            self['ovs_version'] = None
            self['cur_cfg'] = None
            self['uuid'] = None

    def update(self, response):
        if 'result' in response:
            updates = response['result']
        elif 'params' in response:
            updates = response['params'][1]
        else:
            raise NotImplementedError("Invalid updates")

        if 'Interface' in updates:
            self.__update_Interface(updates['Interface'])
            del updates['Interface']
        if 'Port' in updates:
            self.__update_Port(updates['Port'])
            del updates['Port']
        if 'Bridge' in updates:
            self.__update_Bridge(updates['Bridge'])
            del updates['Bridge']
        if 'Open_vSwitch' in updates:
            self.__update_OpenvSwitch(updates['Open_vSwitch'])
            del updates['Open_vSwitch']
        return

    def addBridge(self, bridge):
        self.switch.addBridge(bridge)
        self.bridges[bridge.uuid] = bridge

    def removeBridge(self, bridge_id):
        bridge = self.bridges[bridge_id]
        for uuid, port in list(bridge.ports.items()):
            if not port:
                port = self.ports[uuid]
            for uuid2, interface in list(port.interfaces.items()):
                del port.interfaces[uuid2]
                del self.interfaces[uuid2]
            del bridge.ports[uuid]
            del self.ports[uuid]
        del self.switch.bridges[bridge_id]
        del self.bridges[bridge_id]
        return self.switch

    def removePort(self, port_id):
        port = self.ports[port_id]
        bridge = None
        for uuid, br in list(self.bridges.items()):
            if port_id in br.ports:
                bridge = br
                break
        for uuid, iface in list(port.interfaces.items()):
            if uuid in self.interfaces:
                del self.interfaces[uuid]
        del bridge.ports[port_id]
        del self.ports[port_id]
        return bridge

    def __update_old__(self, requests, response):
        result = response['result']
        requests = self.__sort_Requests(requests)
        for request in requests:
            table = request.name
            if table not in result:
                continue
            if table == OVSTables.OpenvSwitchTable.name:
                self.__update_OpenvSwitch(result[table])
            elif table == OVSTables.BridgeTable.name:
                self.__update_Bridge(result[table])
            elif table == OVSTables.PortTable.name:
                self.__update_Port(result[table])
            elif table == OVSTables.InterfaceTable.name:
                self.__update_Interface(result[table])

    def __sort_Requests(self, requests):
        from enum import Enum
        req_enum = Enum('requests', 'Interface Port Bridge Open_vSwitch')
        if len(req_enum) >= len(requests):
            result = [None]*len(req_enum)
        else:
            result = [None]*len(requests)
        for i in range(0, len(requests)):
            r = requests[i]
            idx = req_enum[r.name].value - 1
            result[idx] = r

        result = [x for x in result if x]
        requests = [req for req in requests if r not in result]
        result.extend(requests)
        return result

    def __update_Interface(self, result):
        for uuid, table_states in list(result.items()):
            self.interfaces[uuid] = OVSInterface.parse(self, uuid, table_states)

    def __update_Port(self, result):
        for uuid, table_states in list(result.items()):
            self.ports[uuid] = OVSPort.parse(self, uuid, table_states)

    def __update_Bridge(self, result):
        for uuid, table_states in list(result.items()):
            self.bridges[uuid] = OVSBridge.parse(self, uuid, table_states)

    def __update_OpenvSwitch(self, result):
        for uuid, table_states in list(result.items()):
            if not self.uuid:
                self['uuid'] = uuid
            self.switch = OVSwitch.parse(self, uuid, table_states)
