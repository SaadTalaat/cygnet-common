

'''
Laying out the Structures of OpenvSwitch Tables
for them to be used into the json rpc requests.

Why is there invalid?
since flag index is indicated by log to base 2,3
both share the value 1 when powered to 0. thus,
zero index should be ommitted
'''
from math import log

class BaseTable(dict):
    columns     = []
    select      = ["invalid","initial","insert","delete","modify"]

    INITIAL     = 3 ** select.index("initial")
    INSERT      = 3 ** select.index("insert")
    DELETE      = 3 ** select.index("delete")
    MODIFY      = 3 ** select.index("modify")

    def __init__(self, *args,**kwargs):
        column_flags = []
        select_flags = []
        if args:
            '''
            Extract both column and select flags
            '''
            column_flags.extend([int(log(flag),2) for flag in args if flag % 2 == 0])
            select_flags.extend([int(log(flag),3) for flag in args if flag % 3 == 0])
        if kwargs:
            column_flags.extend([int(log(flag),2) for flag in kwargs["columns"] if flag % 2 == 0])
            select_flags.extend([int(log(flag),3) for flag in kwargs["select"]  if flag % 3 == 0])

        ## Remove replicated indices
        column_flags = list(set(column_flags))
        select_flags = list(set(select_flags))
        if column_flags:
            self['columns'] = [column for column self.columns if self.columns.index(column) in column_flags]
        if select_flags:
            self['select']  = [op for op in self.select if self.select.index(op) in select_flags]


class PortTable(BaseTable):
    ## TODO: build columns dynamically from a read ovsschema
    ## XXX: not complete
    columns     = ["invalid","interfaces","name","tag","trunks"]

    INTERFACES  = 2 ** columns.index("interfaces")
    NAME        = 2 ** columns.index("name")
    TAG         = 2 ** columns.index("tag")
    TRUNKS      = 2 ** columns.index("trunks")


class ManagerTable(BaseTable):
    columns             = ["invalid","target",
                            "max_backoff","inactivity_probe",
                            "connection_mode","other_config",
                            "external_ids","is_connected",
                            "status"]

    TARGET              = 2 ** columns.index("target")
    MAX_BACKOFF         = 2 ** columns.index("max_backoff")
    INACTIVITY_PROBE    = 2 ** columns.index("inactivity_probe")
    CONNECTION_MODE     = 2 ** columns.index("connection_mode")
    OTHER_CONFIG        = 2 ** columns.index("other_config")
    EXTERNAL_IDS        = 2 ** columns.index("external_ids")
    IS_CONNECTED        = 2 ** columns.index("is_connected")
    STATUS              = 2 ** columns.index("status")

class InterfaceTable(BaseTable):
    ##XXX: not complete
    columns     = ["invalid","name","options","type","mac"]

    NAME        = 2 ** columns.index("name")
    OPTIONS     = 2 ** columns.index("options")
    TYPE        = 2 ** columns.index("type")
    MAC         = 2 ** columns.index("mac")


class BridgeTable(BaseTable):
    columns     = ["invalid","controller","fail_mode","name","ports"]

    CONTROLLER  = 2 ** columns.index("controller")
    FAIL_MODE   = 2 ** columns.index("fail_mode")
    NAME        = 2 ** columns.index("name")
    PORTS       = 2 ** columns.index("ports")


class OpenvSwitchTable(BaseTable):
    columns         = ["invalid","bridges",
                        "cur_cfg","manager_options",
                        "ovs_version"]

    BRIDGES         = 2 ** columns.index("bridges")
    CUR_CFG         = 2 ** columns.index("cur_cfg")
    MANAGER_OPTIONS = 2 ** columns.index("manager_options")
    OVS_VERSION     = 2 ** columns.index("ovs_version")
