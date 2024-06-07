from osha.oira.ploneintranet.interfaces import IQuaiveForm
from zope.interface import implementer


@implementer(IQuaiveForm)
class QuaiveEditFormMixin:
    @property
    def template(self):
        return self.index

    def nextURL(self):
        return f"{self.context.absolute_url()}/@@{self.__name__}"
