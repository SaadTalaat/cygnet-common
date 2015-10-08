from cygnet_common.Structures import BaseDict
from cygnet_common.jsonrpc.helpers.Switch import OVSwitch
from cygnet_common.jsonrpc.helpers.Port import OVSPort
from cygnet_common.jsonrpc.helpers.Bridge import OVSBridge
from cygnet_common.jsonrpc.helpers.Interface import OVSInterface
from uuid import uuid1

class Transaction(BaseDict):


    def __init__(self, op, timeout=0):
        self._instance = None
        self['op'] = op
        self['timeout'] = timeout
        return


    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSwitch, OVSBridge, OVSPort, OVSInterface]
        self._instance = value


class WaitTransaction(Transaction):

    def __init__(self, instance, timeout=0):
        super(WaitTransaction, self).__init__('wait', timeout)
        self['rows'] = list()
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
        self['table'] = {
                OVSPort:'Port',
                OVSBridge:'Bridge',
                OVSwitch: 'Open_vSwitch'
                }[instance_type]

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSwitch, OVSBridge, OVSPort]
        self.table = type(value)
        uuid_row = {
                OVSPort:'interfaces',
                OVSBridge:'ports',
                OVSwitch:'bridges'
                }[type(value)]
        self.rows = {uuid_row:getattr(value, uuid_row)}
        self['columns'].append(uuid_row)
        target = ['uuid', value.uuid]
        condition = ['_uuid','==',target]
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
        for row_name, row_value in row_dict.iteritems():
            row = dict()
            row[row_name] = list()
            [row[row_name].extend(["uuid",uuid]) for uuid in row_value.iterkeys()]
            self['rows'].append(row)


class InsertTransaction(Transaction):

    def __init__(self, instance, timeout=0):
        super(InsertTransaction, self).__init__('insert',timeout)
        self['table'] = None
        self.instance = instance
        self.instance.uuid_name = 'row' + str(uuid1())
        self['uuid-name'] = self.instance.uuid_name

    @property
    def row(self):
        return self['row']

    @row.setter
    def row(self, row_dict):
        self['row'] = dict()
        for column, value in row_dict.iteritems():
            if column in ['ports','interfaces']:
                self['row'][column] = list()
                for entry in value.itervalues():
                    self['row'][column].append('named-uuid')
                    self['row'][column].append(entry.uuid_name)
            else:
                self['row'][column] = value

    @property
    def table(self):
        return self['table']

    @table.setter
    def table(self, instance_type):
        self['table'] = {
                OVSPort: 'Port',
                OVSBridge: 'Bridge',
                OVSInterface: 'Interface'
                }[instance_type]

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
	print type(value), OVSInterface
        assert type(value) in [OVSBridge, OVSPort, OVSInterface]
        self.table = type(value)
        self._instance = value

class MutateTransaction(Transaction):

    def __init__(self, instance, column=None, mutation=None, timeout=0):
        super(MutateTransaction, self).__init__('mutate',timeout)
        self.instance = instance
        self['table'] = None
        self['where'] = list()
        self['mutations'] = list([[column, mutation,1]])

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
        assert type(operation) in [str,unicode]
        assert len(operation) == 2
        assert operation in ["+=","-=","*=","/=","%="]
        if len(self.mutations) == 0:
            self.mutations.append([None,None,None])
        self.mutations[0][1] = operation

    @property
    def column(self):
        return self.mutations[0][0]

    @column.setter
    def column(self, col):
        assert type(col) in [str, unicode]
        assert col in dir(self.instance)
        if len(self.mutations) == 0:
            self.mutations.append([None,None,None])
        self.mutations[0][0] = col

    @property
    def value(self):
        return self.mutations[0][2]

    @value.setter
    def value(self, val):
        if len(self.mutations) == 0:
            self.mutations.append([None,None,None])
        self.mutations[0][2] = val

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSPort, OVSBridge, OVSwitch, OVSInterface]
        self.table = type(value)
        target = ['uuid', value.uuid]
        condition = ['_uuid','==',target]
        self['where'].append(condition)
        self._instance = value

    @property
    def table(self):
        return self['table']
    @table.setter
    def table(self, instance_type):
        self['table'] = {
                OVSPort:    'Port',
                OVSwitch:   'Open_vSwitch',
                OVSBridge:  'Bridge',
                OVSInterface:   'Interface'
                }[instance_type]


class UpdateTransaction(Transaction):

    def __init__(self, instance, column=None, timeout=0):
        super(UpdateTransaction, self).__init__('update',timeout)
        self.instance = instance
        self['table'] = None
        self['where'] = list()
        self['row'] = dict()

    @property
    def row(self):
        return self['row']

    @row.setter
    def row(self, row_dict):
        self['row'] = dict()
        for column, value in row_dict.iteritems():
            if column in ['ports','interfaces','bridges']:
                self['row'][column] = ['set',[]]
                for entry in value.iteritems():
                    if 'uuid_name' in dir(entry):
                        self['row'][column][1].append(['named-uuid',entry.uuid_name])
                    else:
                        self['row'][column][1].append(['uuid',entry.uuid])
            else:
                self['row'][column] = value

    @property
    def table(self):
        return self['table']

    @table.setter
    def table(self, instance_type):
        self['table'] = {
                OVSPort:'Port',
                OVSBridge:'Bridge',
                OVSwitch:'Open_vSwitch',
                OVSInterface:'Interface'
                }[instance_type]

    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, value):
        assert type(value) in [OVSPort,OVSBridge,OVSInterface,OVSwitch]
        self.table = type(value)
        target = ['uuid',value.uuid]
        condition = ['_uuid','==',target]
        self['where'].append(condition)
        self._instance = instance
