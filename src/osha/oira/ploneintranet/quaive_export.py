from euphorie.content.browser.export import ExportSurvey as EuphorieExportSurvey
from osha.oira.ploneintranet.interfaces import IQuaiveForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer


_ = MessageFactory("nuplone")


@implementer(IQuaiveForm)
class QuaiveExportSurvey(EuphorieExportSurvey):
    template = ViewPageTemplateFile("templates/quaive-form.pt")
    label = _("Export OiRA Tool")
    description = ""
    # We don't want to use pat-inject.  It interferes with the download.
    use_injection = False
