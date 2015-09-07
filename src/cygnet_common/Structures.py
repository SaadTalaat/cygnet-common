def hook_function(func):
    def hook(self, *args, **kwargs):
        for callback in self.__callbacks__[func.__name__]:
            callback(*args,**kwargs)
        return func(self, *args, **kwargs)
    return hook

class CallbackList(list):
    append  = hook_function(self.append)
    remove  = hook_function(self.remove)
    pop     = hook_function(self.pop)

    def __init__(self, *args):
        list.__init__(self,*args)
        self.__callbacks__ = {}

    def addCallback(self, func, callback):
        if not self.__callbacks__.has_key(func):
            self.__callbacks__[func.__name__] = [callback]
        self.__callbacks__[func.__name__].append(callback)

    def removeCallback(self, func, callback):
        self.__callbacks__[func.__name__].remove(callback)
