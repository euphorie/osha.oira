from osha.oira.ploneintranet.interfaces import IQuaiveForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
from zope.interface import implementer


@implementer(IQuaiveForm)
class QuaiveFormMixin:

    form_classes = "pat-inject"

    def update(self):
        super().update()
        for group in getattr(self, "groups", []):
            #  This is needed to pick up the custom Quaive widgets
            alsoProvides(group, IQuaiveForm)


@implementer(IQuaiveForm)
class QuaiveEditFormMixin(QuaiveFormMixin):

    @property
    def template(self):
        return self.index

    @property
    def oira_type(self):
        return self.context.portal_type

    def nextURL(self):
        return f"{self.context.absolute_url()}/@@{self.__name__}"

    @property
    def is_edit_form(self):
        """Is this the main edit form or is it some other form?"""
        return self.__name__ == "quaive-edit"


@implementer(IQuaiveForm)
class QuaiveCreateFormMixin(QuaiveFormMixin):
    template = ViewPageTemplateFile("templates/quaive-panel-form.pt")

    @property
    def oira_type(self):
        return self.__name__.rpartition("-")[-1]
