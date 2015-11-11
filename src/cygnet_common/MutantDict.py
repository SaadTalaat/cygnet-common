import collections


class MutantDictBase(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.internal_dict = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self.internal_dict[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.internal_dict[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.internal_dict[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.internal_dict)

    def __len__(self):
        return len(self.internal_dict)

    def __keytransform__(self, key):
        return key
