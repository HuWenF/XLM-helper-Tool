#! /usr/bin/env python

class Singleton(object):
    __instance=None
    def __init__(self):
        #self.Num = Num
        pass
    #def P(self):
        #print(self.Num)
    def __new__(cls,*args,**kwd):
        if Singleton.__instance is None:
            Singleton.__instance=object.__new__(cls,*args,**kwd)
        return cls.__instance



a = Singleton()

print(id(a))

b = Singleton()
print(id(b))


