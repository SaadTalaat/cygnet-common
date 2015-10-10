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
            update = self.update_notification(response)
            if update:
                updates.append(update)
        for response in updates:
            self.ovs_state.update(monitor_requests, response)
        self.cur_id +=1
        return self.ovs_state


    def update_notification(self, notification):
        response = json.loads(notification)
        if response.has_key('method') and response['method'] == 'update':
            print '----------------'
            print '    UPDATE      '
            print '----------------'
            print response
            print '----------------'
            return None
        return response

    def addBridge(self, bridge_name):
        '''
        for adding a bridge, a state much be consistent
        in order to assure consistency, wait transactions are
        conducted on state components (Bridge,Ports)
        '''
        if bridge_name in \
                [br for br in self.ovs_state.bridges.values() if br.name == bridge_name]:

                    return None
        transaction = Transaction(self.cur_id)

        ## Generate Wait operations
        for port,bridge in zip(self.ovs_state.ports.itervalues(), self.ovs_state.bridges.itervalues()):
            transaction.addOperation(WaitOperation(port))
            transaction.addOperation(WaitOperation(bridge))

        ## Build sub-components of a bridge
        intern_if = OVSInterface(bridge_name)
        intern_if.type = 'internal'
        intern_port = OVSPort(bridge_name,[intern_if])
        bridge = OVSBridge(bridge_name,[intern_port])

        ## Generate Insert Operations for built components
        transaction.addOperation(InsertOperation(intern_if))
        transaction.addOperation(InsertOperation(intern_port))
        transaction.addOperation(InsertOperation(bridge))

        switch = self.ovs_state.switch
        switch.addBridge(bridge)
        transaction.addOperation(UpdateOperation(switch,['bridges']))
        transaction.addOperation(MutateOperation(switch,'next_cfg','+='))
        self.sock.send(json.dumps(transaction))

        responses = self.get_responses(self.sock.recv(self.BUFF_SIZE))
        for response in responses:
            result_tmp = self.update_notification(response)
            if result_tmp:
                ## Only one result expected
                result = result_tmp

        print "RESPONSE"
        print result
        self.cur_id +=1
        from pprint import pprint
        pprint(transaction)


    def cancel_transact(self, transact_id):
        pass

    def cancel_monitor(self):
        pass

