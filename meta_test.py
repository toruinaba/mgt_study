from abc import ABCMeta, abstractmethod


class A(object):
    __metaclass__ = ABCMeta

    @abstractmethod        
    def require_override(self): pass


class BMeta(type):
    def __new__(mcls, name, bases, attrs):
        cls = super(BMeta, mcls).__new__(mcls, name, bases, attrs)
        cls.b = 2
        return cls


def BMetaFunc(name, bases, attrs):
    cls = type(name, bases, attrs)
    cls.b = 2
    return cls


class B(A):
    __metaclass__ = BMetaFunc
        
    @abstractmethod
    def require_override_b(self): pass

class C(B):
    def require_override(self):
        return 3

    def require_override_b(self):
        return 2


c = C()
assert c.b == 2
assert c.require_override() == 3
assert c.require_override_b() == 2
assert c.value == 1