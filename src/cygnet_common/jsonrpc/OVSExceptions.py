

class OVSException(Exception):
    pass


class OVSUnsupportedProtocol(OVSException):

    def __init__(self, message=None):
        if not message:
            super(OVSUnsupportedProtocol, self).__init__('only TCP and unix sockets are supported')
        else:
            super(OVSUnsupportedProtocol, self).__init__(message)


class OVSTransactionFailed(OVSException):
    def __init__(self, result):
        message = result[-1]['error']
        details = result[-1]['details']
        super(OVSTransactionFailed, self).__init__(message + ':' + details)


class OVSBridgeExists(OVSException):
    def __init__(self, bridge_name):
        super(OVSBridgeExists, self).__init__('Bridge ' + bridge_name + ' already Exists')


class OVSPortExists(OVSException):
    def __init__(self, port_name):
        super(OVSPortExists, self).__init__('Port ' + port_name + ' already Exists')


class OVSNoSuchBridge(OVSException):
    def __init__(self, bridge_name):
        super(OVSNoSuchBridge, self).__init__('Bridge ' + bridge_name + ' does not exist')


class OVSNoSuchPort(OVSException):
    def __init__(self, port_name):
        super(OVSNoSuchPort, self).__init__('Port ' + port_name + ' does not exist')


class OVSInvalidInstance(OVSException):
    def __init__(self, message=None):
        if not message:
            super(OVSInvalidInstance, self).__init__('instance must be switch,bridge,port or interface')
        else:
            super(OVSInvalidInstance, self).__init__(message)
