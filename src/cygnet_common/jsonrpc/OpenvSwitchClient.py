import socket
import json
from cygnet_common.jsonrpc.OpenvSwitchTables import *
from cygnet_common.jsonrpc.OpenvSwitchState import OpenvSwitchState
from cygnet_common.jsonrpc.operations.Transaction import *
from cygnet_common.jsonrpc.helpers.Bridge import OVSBridge
from cygnet_common.jsonrpc.helpers.Port import OVSPort
from cygnet_common.jsonrpc.helpers.Interface import OVSInterface

class OpenvSwitchClient(object):

    BUFF_SIZE = 32768
    def __init__(self, db_peer):
        if type(db_peer) not in [str,unicode]:
            raise TypeError,"Database address should be in string format"

        protocol = db_peer[:db_peer.find('//')-1]

        if protocol == 'unix':
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect( db_peer[ db_peer.find('//') + 2 :] )

        elif protocol == 'tcp':
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect( tuple( db_peer[ db_peer.find('//') + 2 :].split(":") ) )

        else:
            raise NotImplementedError

        self.cur_id = 0
        self.monitor_id = None
        self.ovs_state = OpenvSwitchState()
    def get_responses(self, response_str):
        objects = []
        while response_str.find('}{') != -1:
            obj = response_str[:response_str.find('}{')+1]
            objects.append(obj)
            response_str = response_str[len(obj):]
        objects.append(response_str)
        return objects

    def getState(self, monitor_requests):
        ### Monitor params should be:
        ##  - Tables
        updates = []
        response = None
        params = [
                "Open_vSwitch",
                None,
                dict()]
        for request in monitor_requests:
            params[2][request.name] = request

        payload = {
                'method'    :'monitor',
                'id'        :self.cur_id,
                'params'    : params
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
            #self.ovs_state.update(monitor_requests, response)
            self.ovs_state.update(response)
        self.cur_id +=1
        return self.ovs_state


    def update_notification(self, response):
        if response.has_key('method') and response['method'] == 'update':
            print "UPDATE",response
            self.ovs_state.update(response)
            return None
        return response

    def addBridge(self, bridge_name):
        '''
        for adding a bridge, a state much be consistent
        in order to assure consistency, wait transactions are
        conducted on state components (Bridge,Ports)
        '''
        switch = self.ovs_state.switch
        if bridge_name in \
                [br.name for br in self.ovs_state.bridges.values() if br.name == bridge_name]:

                    return None
        transaction = Transaction(self.cur_id)

        ## Generate Wait operations
        for instance in self.ovs_state.ports.values() + self.ovs_state.bridges.values():
            transaction.addOperation(WaitOperation(instance))

        ## Build sub-components of a bridge
        intern_if = OVSInterface(bridge_name)
        intern_if.type = 'internal'
        intern_port = OVSPort(bridge_name,[intern_if])
        bridge = OVSBridge(bridge_name,[intern_port])

        ## Generate Insert Operations for built components
        transaction.addOperation(InsertOperation(intern_if))
        transaction.addOperation(InsertOperation(intern_port))
        transaction.addOperation(InsertOperation(bridge))

        switch.addBridge(bridge)
        transaction.addOperation(UpdateOperation(switch,['bridges']))
        transaction.addOperation(MutateOperation(switch,'next_cfg','+='))
        self.sock.send(json.dumps(transaction))
        del switch.bridges[bridge.uuid]
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))

        for response in responses:
            res = json.loads(response)
            transaction.handleResult(res)
            self.update_notification(res)
        from pprint import pprint
        pprint(self.ovs_state.bridges)
        #print "RESPONSE"
        #print responses
        self.cur_id +=1
        #pprint(transaction)

    def removeBridge(self, bridge_name):
        print 'DELETEING', bridge_name
        switch = self.ovs_state.switch
        bridge = None
        if bridge_name in \
                [br.name for br in switch.bridges.values()]:
                    bridge = [br for br in switch.bridges.values() if br.name == bridge_name][0]

        transaction = Transaction(self.cur_id)
        transaction.addOperation(WaitOperation(switch))
        self.ovs_state.removeBridge(bridge.uuid)
        transaction.addOperation(UpdateOperation(switch,['bridges']))
        transaction.addOperation(MutateOperation(switch,'next_cfg','+='))
        self.sock.send(json.dumps(transaction))
        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))

        for response in responses:
            res = json.loads(response)
            transaction.handleResult(res)
            #self.update_notification(res)

        self.cur_id += 1

    def cancel_transact(self, transact_id):
        pass

    def cancel_monitor(self):
        pass

