from osha.oira.ploneintranet.interfaces import IQuaiveForm
from plone.dexterity.browser.edit import DefaultEditForm
from zope.interface import implementer


@implementer(IQuaiveForm)
class QuaiveEditFormMixin:
    @property
    def template(self):
        return self.index

    def nextURL(self):
        return f"{self.context.absolute_url()}/@@{self.__name__}"


class SurveyQuaiveVersionsForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SurveyGroupQuaiveVersionsForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""
