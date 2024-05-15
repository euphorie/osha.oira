from osha.oira.content.browser.sector import AddView as EuphorieSectorAddView
from osha.oira.ploneintranet.interfaces import IQuaiveForm
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


@implementer(IQuaiveForm)
class QuaiveCreateFormMixin:
    template = ViewPageTemplateFile("templates/quaive-create.pt")

    def nextURL(self):
        """We want to redirect to the quaive edit form"""
        next_url = super().nextURL()
        return f"{next_url}/@@quaive-edit"


class QuaiveCreateViewMixin:

    def __init__(self, context, request):
        portal_type = self.__name__.rpartition("-")[-1]
        fti = api.portal.get_tool("portal_types")[portal_type]
        super().__init__(context, request, fti)


class QuaiveCreateEuphorieSectorForm(QuaiveCreateFormMixin, EuphorieSectorAddView.form):
    pass


class QuaiveCreateEuphorieSectorView(QuaiveCreateViewMixin, EuphorieSectorAddView):

    form = QuaiveCreateEuphorieSectorForm
