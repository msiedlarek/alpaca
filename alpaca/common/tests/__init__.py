class InterfaceTestMixin:

    def assertClassImplements(self, class_, interface):
        from zope.interface.verify import verifyClass
        verifyClass(interface, class_)

    def assertObjectImplements(self, object_, interface):
        from zope.interface.verify import verifyObject
        verifyObject(interface, object_)
