def hook_function(func):
    def hook(self, *args, **kwargs):
        for callback in self.__callbacks__[func.__name__]:
            callback(*args, **kwargs)
        return func(self, *args, **kwargs)
    return hook


class CallbackList(list):
    append = hook_function(list.append)
    remove = hook_function(list.remove)
    pop = hook_function(list.pop)

    def __init__(self, *args):
        list.__init__(self, *args)
        self.__callbacks__ = {}

    def addCallback(self, func, callback):
        if func not in self.__callbacks__:
            self.__callbacks__[func.__name__] = [callback]
            return
        self.__callbacks__[func.__name__].append(callback)

    def removeCallback(self, func, callback):
        self.__callbacks__[func.__name__].remove(callback)


class BaseDict(dict):
    def __getattribute__(self, key, *args):
        try:
            return dict.__getattribute__(self, key)
        except AttributeError as e:
            if key in self:
                return self[key]
            else:
                raise e

    def __setattr__(self, key, value):
        try:
            dict.__setattr__(self, key, value)
        except AttributeError as e:
            if key in self:
                self[key] = value
            else:
                raise e

    def __delattr__(self, key):
        try:
            dict.__delattr__(self, key)
        except AttributeError as e:
            if key in self:
                del self[key]
            else:
                raise e
