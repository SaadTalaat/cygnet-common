from cygnet_common.jsonrpc import OVSExceptions
from uuid import uuid1


class OVSField(property):
    pass


class OVSAtom(list):

    def __init__(self, l=None):
        if l and len(l) > 2:
            raise OVSExceptions.OVSValueError("Atom shouldn't be more than 2 fields")
        super(OVSAtom, self).__init__(l)

    def append(self, val):
        if len(self) >= 2:
            raise IndexError("atom can only contain two members")
        super(OVSAtom, self).append(val)


class OVSMap(list):

    def __init__(self, l=None):
        super(OVSMap, self).__init__()
        super(OVSMap, self).append('map')
        super(OVSMap, self).append([])
        if isinstance(l, list):
            if l[0] == 'map':
                for member in l[1]:
                    self.append(member)
                    return
        elif not l:
            return
        else:
            raise TypeError("Value must be a list of OVSAtoms")

    def append(self, atom):
        self[1].append(atom)


class OVSSet(list):

    def __init__(self, l=None):
        if isinstance(l, list):
            if len(l) > 1:
                self[0] = 'set'
            for member in l:
                if member == 'set':
                    continue
                self.append(member)
        if not l:
            self.append('set')
            self.append([])
        else:
            raise TypeError("Value must be a list of OVSAtoms")

    def append(self, atom):
        if not isinstance(atom, OVSAtom):
            raise OVSExceptions.OVSValueError("value must be an OVSAtom")
        if len(self) == 2 and self[0] == 'set':
            self = []
            for val in atom:
                super(OVSSet, self).append(val)
            return

        elif len(self) == 2 and self[0] != 'set':
            tmp_atom = [self[0], self[1]]
            self = []
            self.append('set')
            self.append(tmp_atom)
            self.append(atom)
            return

        super(OVSSet, self).append(atom)

    def insert(self, index, atom):
        if not isinstance(atom, OVSAtom):
            raise OVSExceptions.OVSValueError("value must be an OVSAtom")
        super(OVSSet, self).insert(index, atom)

    def remove(self, val):
        isAtom = False
        if val == 'set':
            raise OVSExceptions.OVSValueError("scalar value can't be removed")
        if len(self) == 3 and self[0] == 'set':
            isAtom = True
        super(OVSSet, self).remove(val)
        if isAtom:
            self = self[1]

    def pop(self, index):
        if index == 0:
            raise OVSExceptions.OVSValueError("scalar value can't be removed")
        super(OVSSet, self).pop(index)


class OVSUUID(OVSAtom):

    def __init__(self, uuid=None):
        if type(uuid) in [str, str]:
            super(OVSUUID, self).__init__(['uuid', uuid])
        elif isinstance(uuid, list) and uuid[0] == 'uuid':
            super(OVSUUID, self).__init__(uuid)
        elif not uuid:
            super(OVSUUID, self).__init__(['uuid', ''])
        else:
            raise TypeError("value must be a list,string or NoneType")

    @property
    def uuid(self):
        return self[1]


class OVSNUUID(OVSAtom):

    def __init__(self, uuid=None):
        if type(uuid) in [str, str]:
            super(OVSNUUID, self).__init__(['named-uuid'])
        elif isinstance(uuid, list) and uuid[0] == 'named-uuid':
            super(OVSNUUID, self).__init__(uuid)
        elif not uuid:
            row_uuid = 'row' + str(uuid1()).replace('-', '_')
            super(OVSNUUID, self).__init__(['named-uuid', row_uuid])
        else:
            raise TypeError("value must be a list, string or NoneType")

    @property
    def uuid(self):
        return self[1]
