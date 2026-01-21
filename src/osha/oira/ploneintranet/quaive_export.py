from euphorie.content.browser.export import ExportSurvey as EuphorieExportSurvey
from osha.oira.ploneintranet.interfaces import IQuaiveForm
from osha.oira.ploneintranet.quaive_mixin import QuaiveFormMixin
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer


_ = MessageFactory("nuplone")


@implementer(IQuaiveForm)
class QuaiveExportSurvey(QuaiveFormMixin, EuphorieExportSurvey):
    template = ViewPageTemplateFile("templates/quaive-form.pt")
    label = _("Export OiRA Tool")
    description = ""
    # Empty the form classes.  Specifically we don't want to use pat-inject,
    # as it interferes with the download.
    form_classes = ""
