import socket
import json
from cygnet_common.jsonrpc import OpenvSwitchTables

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

    def monitor(self, monitor_requests):
        ### Monitor params should be:
        ##  - Tables
        params = [
                "Open_vSwitch",
                None,
                dict()]
        for request in monitor_requests:
            params[2][request.__class__.__name__] = request

        payload = {
                'method'    :'monitor',
                'id'        :self.cur_id,
                'params'    : params
                }
        self.sock.send(json.dumps(payload))

        self.monitor = self.cur_id
        while True:
            ## is it a notification?
            response = self.update_notification(self.sock.recv(self.BUFF_SIZE))
            if response:
                break
        self.ovs_state.update(monitor_requests, response)
        self.cur_id +=1
        return self.ovs_state


    def update_notification(self, notification):
        '''
        validate notification
        if not notification just return back the data passed
        '''
        pass

    def transaction(self, operations):
        pass

    def cancel_transact(self, transact_id):
        pass

    def cancel_monitor(self):
        pass

