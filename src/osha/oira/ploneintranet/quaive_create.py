from euphorie.content.browser.country import AddView as EuphorieCountryAddView
from euphorie.content.browser.module import AddView as EuphorieModuleAddView
from euphorie.content.browser.survey import AddView as EuphorieSurveyAddView
from euphorie.content.browser.surveygroup import AddView as EuphorieSurveyGroupAddView
from osha.oira.content.browser.risk import AddView as EuphorieRiskAddView
from osha.oira.content.browser.sector import AddView as EuphorieSectorAddView
from osha.oira.content.browser.solution import AddView as EuphorieSolutionAddView
from osha.oira.ploneintranet.interfaces import IQuaiveForm
from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer


@implementer(IQuaiveForm)
class QuaiveCreateFormMixin:
    template = ViewPageTemplateFile("templates/quaive-create.pt")

    def nextURL(self):
        """We want to redirect to the quaive edit form

        We try to sniff from the referer where to redirect the user to.

        If we fail, we server the default.
        """
        referer = self.request.getHeader("HTTP_REFERER")
        if referer:
            referer = referer.replace("@@", "")
            if "/panel-oira-remote-create/" in referer:
                referer = referer.partition("?")[0]
                base_url, path = referer.partition("/panel-oira-remote-create/")[::2]
                new_obj_id = self.immediate_view.rpartition("/")[-1]
                return f"{base_url}/@@oira-edit/{path}/{new_obj_id}"

        return super().nextURL()


class QuaiveCreateViewMixin:
    def __init__(self, context, request):
        portal_type = self.__name__.rpartition("-")[-1]
        fti = api.portal.get_tool("portal_types")[portal_type]
        super().__init__(context, request, fti)


class QuaiveCreateEuphorieSectorForm(QuaiveCreateFormMixin, EuphorieSectorAddView.form):
    pass


class QuaiveCreateEuphorieSectorView(QuaiveCreateViewMixin, EuphorieSectorAddView):
    form = QuaiveCreateEuphorieSectorForm


class QuaiveCreateEuphorieCountryForm(
    QuaiveCreateFormMixin, EuphorieCountryAddView.form
):
    pass


class QuaiveCreateEuphorieCountryView(QuaiveCreateViewMixin, EuphorieCountryAddView):
    form = QuaiveCreateEuphorieCountryForm


class QuaiveCreateEuphorieRiskForm(QuaiveCreateFormMixin, EuphorieRiskAddView.form):
    pass


class QuaiveCreateEuphorieRiskView(QuaiveCreateViewMixin, EuphorieRiskAddView):
    form = QuaiveCreateEuphorieRiskForm


class QuaiveCreateEuphorieSurveyGroupForm(
    QuaiveCreateFormMixin, EuphorieSurveyGroupAddView.form
):
    pass


class QuaiveCreateEuphorieSurveyGroupView(
    QuaiveCreateViewMixin, EuphorieSurveyGroupAddView
):
    form = QuaiveCreateEuphorieSurveyGroupForm


class QuaiveCreateEuphorieSurveyForm(QuaiveCreateFormMixin, EuphorieSurveyAddView.form):
    pass


class QuaiveCreateEuphorieSurveyView(QuaiveCreateViewMixin, EuphorieSurveyAddView):
    form = QuaiveCreateEuphorieSurveyForm


class QuaiveCreateEuphorieModuleForm(QuaiveCreateFormMixin, EuphorieModuleAddView.form):
    pass


class QuaiveCreateEuphorieModuleView(QuaiveCreateViewMixin, EuphorieModuleAddView):
    form = QuaiveCreateEuphorieModuleForm


class QuaiveCreateEuphorieSolutionForm(
    QuaiveCreateFormMixin, EuphorieSolutionAddView.form
):
    pass


class QuaiveCreateEuphorieSolutionView(QuaiveCreateViewMixin, EuphorieSolutionAddView):
    form = QuaiveCreateEuphorieSolutionForm
