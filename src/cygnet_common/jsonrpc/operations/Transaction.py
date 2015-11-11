from cygnet_common.Structures import BaseDict
from cygnet_common.jsonrpc.helpers.Switch import OVSwitch
from cygnet_common.jsonrpc.helpers.Port import OVSPort
from cygnet_common.jsonrpc.helpers.Bridge import OVSBridge
from cygnet_common.jsonrpc.helpers.Interface import OVSInterface
from cygnet_common.jsonrpc import OVSExceptions


class Transaction(BaseDict):

    def __init__(self, cur_id=0):
        self['method'] = 'transact'
        self['id'] = cur_id
        self['params'] = ['Open_vSwitch']

    def addOperation(self, operation):
        if isinstance(operation, Operation):
            self.params.append(operation)

    def delOperation(self, operation):
        if operation in self.params and isinstance(operation, Operation):
            del self.params[self.params.index(operation)]

    def addOperations(self, *args):
        for operation in args:
            if isinstance(operation, Operation):
                self.params.append(operation)

    def handleResult(self, response):
        if 'result' not in response:
            return
        print(response)
        result = response['result']
        if 'error' in result[-1]:
            raise OVSExceptions.OVSTransactionFailed(result)
        for index, param in enumerate(self.params[1:]):
            param.handleResult(result[index])


class Operation(BaseDict):

    def __init__(self, op):
        self._instance = None
        self['op'] = op

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        if type(value) in [OVSwitch, OVSBridge, OVSPort, OVSInterface]:
            raise OVSExceptions.OVSInvalidInstance
        self._instance = value

    def handleResult(self, result):
        pass


class WaitOperation(Operation):

    def __init__(self, instance, timeout=0):
        super(WaitOperation, self).__init__('wait')
        self['rows'] = list()
        self['timeout'] = timeout
        self['columns'] = list()
        self['until'] = '=='
        self['where'] = list()
        self['table'] = None
        self.instance = instance

    @property
    def table(self):
        return self['table']

    @table.setter
    def table(self, instance_type):
        self['table'] = {OVSPort: 'Port',
                         OVSBridge: 'Bridge',
                         OVSwitch: 'Open_vSwitch'
                         }[instance_type]

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSwitch, OVSBridge, OVSPort]
        self.table = type(value)
        uuid_row = {OVSPort: 'interfaces',
                    OVSBridge: 'ports',
                    OVSwitch: 'bridges'
                    }[type(value)]
        self.rows = {uuid_row: getattr(value, uuid_row)}
        self['columns'].append(uuid_row)
        target = ['uuid', value.uuid]
        condition = ['_uuid', '==', target]
        self['where'].append(condition)
        self._instance = value

    @property
    def rows(self):
        return self['rows']

    @rows.setter
    def rows(self, row_dict):
        '''
        Since Instance is always either Port, Bridge, Switch
        The row_value is always going to be a dict holding
        uuids of its network substances and itself.
        '''
        self['rows'] = list()
        for row_name, row_value in list(row_dict.items()):
            row = dict()
            row[row_name] = list()
            if len(row_value) == 1:
                [row[row_name].extend(["uuid", uuid]) for uuid in list(row_value.keys())]
            else:
                row[row_name].extend(['set', []])
                [row[row_name][1].extend([["uuid", uuid]]) for uuid in list(row_value.keys())]
            self['rows'].append(row)


class InsertOperation(Operation):

    def __init__(self, instance):
        super(InsertOperation, self).__init__('insert')
        self['table'] = None
        self.instance = instance
        self['uuid-name'] = self.instance.uuid_name

    @property
    def row(self):
        return self['row']

    @row.setter
    def row(self, row_dict):
        self['row'] = dict()
        for column, value in list(row_dict.items()):
            if column in ['ports', 'interfaces']:
                self['row'][column] = list()
                for entry in list(value.values()):
                    self['row'][column].append('named-uuid')
                    self['row'][column].append(entry.uuid_name)
            else:
                self['row'][column] = value

    @property
    def table(self):
        return self['table']

    @table.setter
    def table(self, instance_type):
        self['table'] = {OVSPort: 'Port',
                         OVSBridge: 'Bridge',
                         OVSInterface: 'Interface'
                         }[instance_type]

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSBridge, OVSPort, OVSInterface]
        self.table = type(value)
        self.row = value.columns
        self._instance = value

    def handleResult(self, result):
        if 'uuid' in result:
            self.instance.uuid = str(result['uuid'][1])
            del self.instance.uuid_name


class MutateOperation(Operation):

    def __init__(self, instance, column=None, mutation=None):
        super(MutateOperation, self).__init__('mutate')
        self['table'] = None
        self['where'] = list()
        self['mutations'] = list([[column, mutation, 1]])
        self.instance = instance

    @property
    def mutations(self):
        return self['mutations'][0]

    @mutations.setter
    def mutations(self, mutate_list):
        self['mutations'].append(list())
        self['mutations'][0].append(mutate_list[0])
        self['mutations'][0].append(mutate_list[1])
        self['mutations'][0].append(mutate_list[2])

    @property
    def mutation(self):
        return self._mutation

    @mutation.setter
    def mutation(self, operation):
        assert type(operation) in [str, str]
        assert len(operation) == 2
        assert operation in ["+=", "-=", "*=", "/=", "%="]
        if len(self.mutations) == 0:
            self.mutations.append([None, None, None])
        self.mutations[0][1] = operation

    @property
    def column(self):
        return self.mutations[0][0]

    @column.setter
    def column(self, col):
        assert type(col) in [str, str]
        assert col in dir(self.instance)
        if len(self.mutations) == 0:
            self.mutations.append([None, None, None])
        self.mutations[0][0] = col

    @property
    def value(self):
        return self.mutations[0][2]

    @value.setter
    def value(self, val):
        if len(self.mutations) == 0:
            self.mutations.append([None, None, None])
        self.mutations[0][2] = val

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSPort, OVSBridge, OVSwitch, OVSInterface]
        self.table = type(value)
        target = ['uuid', value.uuid]
        condition = ['_uuid', '==', target]
        self['where'].append(condition)
        self._instance = value

    @property
    def table(self):
        return self['table']

    @table.setter
    def table(self, instance_type):
        self['table'] = {OVSPort:    'Port',
                         OVSwitch:   'Open_vSwitch',
                         OVSBridge:  'Bridge',
                         OVSInterface:   'Interface'
                         }[instance_type]


class UpdateOperation(Operation):

    def __init__(self, instance, column=None):
        super(UpdateOperation, self).__init__('update')
        self['table'] = None
        self['where'] = list()
        self['row'] = dict()
        self.up_col = column
        self.instance = instance

    @property
    def row(self):
        return self['row']

    @row.setter
    def row(self, row_dict):
        for column, value in list(row_dict.items()):
            if column == 'name':
                continue
            elif column in ['ports', 'interfaces', 'bridges']:
                self['row'][column] = ['set', []]
                for entry_id, entry in list(value.items()):
                    if entry_id[:3] == 'row':
                        self['row'][column][1].append(['named-uuid', entry.uuid_name])
                    else:
                        self['row'][column][1].append(['uuid', entry.uuid])
            else:
                self['row'][column] = value

    @property
    def table(self):
        return self['table']

    @table.setter
    def table(self, instance_type):
        self['table'] = {OVSPort: 'Port',
                         OVSBridge: 'Bridge',
                         OVSwitch: 'Open_vSwitch',
                         OVSInterface: 'Interface'
                         }[instance_type]

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSPort,
                               OVSBridge,
                               OVSInterface,
                               OVSwitch]
        self.table = type(value)
        target = ['uuid', value.uuid]
        condition = ['_uuid', '==', target]
        self['where'].append(condition)
        if self.up_col and type(self.up_col) in [str, str]:
            self.row = {self.up_col: value.columns[self.up_col]}
        elif self.up_col and isinstance(self.up_col, list):
            rows = []
            for col in self.up_col:
                rows.append((col, value.columns[col]))
            self.row = dict(rows)
        else:
            self.row = value.columns
        self._instance = value
