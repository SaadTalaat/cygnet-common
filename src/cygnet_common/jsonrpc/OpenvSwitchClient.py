import socket
import json
from cygnet_common.jsonrpc.OpenvSwitchState import OpenvSwitchState
from cygnet_common.jsonrpc.operations.Transaction import Transaction, MutateOperation, UpdateOperation, WaitOperation, InsertOperation
from cygnet_common.jsonrpc.helpers.Bridge import OVSBridge
from cygnet_common.jsonrpc.helpers.Port import OVSPort
from cygnet_common.jsonrpc.helpers.Interface import OVSInterface
from cygnet_common.jsonrpc import OVSExceptions


class OpenvSwitchClient(object):

    BUFF_SIZE = 32768
    cur_id = 0

    def __init__(self, db_peer=None):
        if type(db_peer) not in [str, unicode] and not self.db_peer:
            raise TypeError("Database address should be in string format")

        protocol = db_peer[:db_peer.find('//')-1]

        if protocol == 'unix':
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(db_peer[db_peer.find('//') + 2:])

        elif protocol == 'tcp':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(tuple(db_peer[db_peer.find('//') + 2:].split(":")))

        else:
            raise OVSExceptions.OVSUnsupportedProtocol

        self.monitor_id = None
        self.ovs_state = OpenvSwitchState()

    def commit(self, transaction):
        if not isinstance(transaction, Transaction):
            raise OVSExceptions.OVSValueError("Unexpected Transaction Value")
        self.sock.send(json.dumps(transaction))
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        for response in responses:
            res = json.loads(response)
            transaction.handleResult(res)
            self.update_notification(res)
        self.cur_id += 1

    def get_responses(self, response_str):
        objects = []
        while response_str.find('}{') != -1:
            obj = response_str[:response_str.find('}{')+1]
            objects.append(obj)
            response_str = response_str[len(obj):]
        objects.append(response_str)
        return objects

    def getState(self, monitor_requests):
        # Monitor params should be:
        #  - Tables
        updates = []
        response = None
        params = ["Open_vSwitch", None, dict()]
        for request in monitor_requests:
            params[2][request.name] = request

        payload = {'method': 'monitor',
                   'id': self.cur_id,
                   'params': params
                   }
        self.sock.send(json.dumps(payload))

        self.monitor_id = self.cur_id
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        for response in responses:
            res = json.loads(response)
            update = self.update_notification(res)
            if update:
                updates.append(update)
        for response in updates:
            self.ovs_state.update(response)
        self.cur_id += 1
        return self.ovs_state

    def update_notification(self, response):
        if 'method' in response and response['method'] == 'update':
            self.ovs_state.update(response)
            return None
        return response

    def addBridge(self, bridge_name):
        switch = self.ovs_state.switch
        if bridge_name in \
                [br.name for br in self.ovs_state.bridges.values() if br.name == bridge_name]:
                    raise OVSExceptions.OVSBridgeExists(bridge_name)

        transaction = Transaction(self.cur_id)

        # Generate Wait operations
        for instance in self.ovs_state.ports.values() + self.ovs_state.bridges.values():
            transaction.addOperation(WaitOperation(instance))

        # Build sub-components of a bridge
        intern_if = OVSInterface(bridge_name)
        intern_if.type = 'internal'
        intern_port = OVSPort(bridge_name, [intern_if])
        bridge = OVSBridge(bridge_name, [intern_port])

        # Generate Insert Operations for built components
        transaction.addOperation(InsertOperation(intern_if))
        transaction.addOperation(InsertOperation(intern_port))
        transaction.addOperation(InsertOperation(bridge))

        switch.addBridge(bridge)
        transaction.addOperation(UpdateOperation(switch, ['bridges']))
        transaction.addOperation(MutateOperation(switch, 'next_cfg', '+='))
        self.sock.send(json.dumps(transaction))
        del switch.bridges[bridge.uuid]
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        print responses
        for response in responses:
            res = json.loads(response)
            transaction.handleResult(res)
            self.update_notification(res)
        self.cur_id += 1

    def removeBridge(self, bridge_name):
        switch = self.ovs_state.switch
        bridge = None
        if bridge_name in \
                [br.name for br in switch.bridges.values()]:
                    bridge = [br for br in switch.bridges.values() if br.name == bridge_name][0]
        else:
            raise OVSExceptions.OVSNoSuchBridge(bridge_name)

        transaction = Transaction(self.cur_id)
        transaction.addOperation(WaitOperation(switch))
        self.ovs_state.removeBridge(bridge.uuid)
        transaction.addOperation(UpdateOperation(switch, ['bridges']))
        transaction.addOperation(MutateOperation(switch, 'next_cfg', '+='))
        self.sock.send(json.dumps(transaction))
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))

        for response in responses:
            res = json.loads(response)
            transaction.handleResult(res)
        self.cur_id += 1

    def bridgeExists(self, br_name):
        if br_name in \
                [br.name for br in self.ovs_state.bridges.itervalues()]:
                    return True
        return False

    def portExists(self, port_name):
        if port_name in \
                [port.name for port in self.ovs_state.ports.itervalues()]:
                    return True
        return False

    def interfaceExists(self, if_name):
        if if_name in \
                [iface.name for iface in self.ovs_state.interfaces.itervalues()]:
                    return True
        return False

    def addPort(self, bridge_name, port_name):
        if bridge_name not in \
                [br.name for br in self.ovs_state.bridges.itervalues()]:
                    raise OVSExceptions.OVSNoSuchBridge(bridge_name)
        if port_name in \
                [port.name for port in self.ovs_state.ports.itervalues()]:
                    raise OVSExceptions.OVSPortExists(port_name)

        transaction = Transaction(self.cur_id)
        for instance in self.ovs_state.bridges.values() + self.ovs_state.ports.values():
            transaction.addOperation(WaitOperation(instance))
        switch = self.ovs_state.switch
        iface = OVSInterface(port_name)
        port = OVSPort(port_name, [iface])
        transaction.addOperation(InsertOperation(iface))
        transaction.addOperation(InsertOperation(port))
        bridge = None
        for br in self.ovs_state.bridges.itervalues():
            if br.name == bridge_name:
                bridge = br
                break
        bridge.ports[port.uuid] = port
        transaction.addOperation(UpdateOperation(bridge, 'ports'))
        transaction.addOperation(MutateOperation(switch, 'next_cfg', '+='))
        self.sock.send(json.dumps(transaction))
        del bridge.ports[port.uuid]
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        for response in responses:
            res = json.loads(response)
            transaction.handleResult(res)
            self.update_notification(res)
        self.cur_id += 1
        return True

    def removePort(self, port_name):
        if port_name not in \
                [port.name for port in self.ovs_state.ports.itervalues()]:
                    raise OVSExceptions.OVSNoSuchPort(port_name)

        switch = self.ovs_state.switch
        transaction = Transaction(self.cur_id)
        for instance in self.ovs_state.bridges.values() + self.ovs_state.ports.values():
            transaction.addOperation(WaitOperation(instance))

        port = None
        for p in self.ovs_state.ports.itervalues():
            if p.name == port_name:
                port = p
                break
        bridge = self.ovs_state.removePort(port.uuid)
        transaction.addOperation(UpdateOperation(bridge, 'ports'))
        transaction.addOperation(MutateOperation(switch, 'next_cfg', '+='))
        self.sock.send(json.dumps(transaction))

        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        for response in responses:
            res = json.loads(response)
            transaction.handleResult(res)
        self.cur_id += 1
        return True

    def getBridge(self, bridge_name):
        for bridge in self.ovs_state.bridges.itervalues():
            if bridge.name == bridge_name:
                return bridge
        raise IndexError("No such bridge")

    def getPort(self, port_name):
        for port in self.ovs_state.ports.itervalues():
            if port.name == port_name:
                return port
        raise IndexError("No such port")

    def getInterface(self, interface_name):
        for interface in self.ovs_state.interfaces.itervalues():
            if interface.name == interface_name:
                return interface
        raise IndexError("No such port")

    def setBridgeProperty(self, bridge_name, option, value):
        bridge = self.getBridge(bridge_name)
        if hasattr(bridge, option):
            setattr(bridge, option, value)
        t = Transaction(self.cur_id)
        t.addOperation(WaitOperation(bridge))
        t.addOperation(UpdateOperation(bridge))
        t.addOperation(MutateOperation(self.ovs_state.switch, 'next_cfg', '+='))
        self.sock.send(json.dumps(t))

        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        for response in responses:
            res = json.loads(response)
            t.handleResult(res)
            self.update_notification(res)
        self.cur_id += 1

    def setPortProperty(self, port_name, option, value):
        port = self.getPort(port_name)
        if hasattr(port, option):
            setattr(port, option, value)
        t = Transaction(self.cur_id)
        t.addOperation(WaitOperation(port))
        t.addOperation(UpdateOperation(port))
        t.addOperation(MutateOperation(self.ovs_state.switch, 'next_cfg', '+='))
        self.sock.send(json.dumps(t))

        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        for response in responses:
            res = json.loads(response)
            t.handleResult(res)
            self.update_notification(res)
        self.cur_id += 1

    def setInterfaceProperty(self, interface_name, option, value):
        interface = self.getInterface(interface_name)
        if hasattr(interface, option):
            print 'VALUE', value
            setattr(interface, option, value)

        t = Transaction(self.cur_id)
        t.addOperation(UpdateOperation(interface))
        t.addOperation(MutateOperation(self.ovs_state.switch, 'next_cfg', '+='))
        self.sock.send(json.dumps(t))
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        print "OPTIONS:", interface.columns
        for response in responses:
            res = json.loads(response)
            t.handleResult(res)
            self.update_notification(res)
        interface = self.getInterface(interface_name)
        self.cur_id += 1

    def cancel_transact(self, transact_id):
        pass

    def cancel_monitor(self):
        pass
