from euphorie.content.browser.upload import ImportSurvey as EuphorieImportSurvey
from osha.oira.ploneintranet.interfaces import IQuaiveForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer


_ = MessageFactory("nuplone")


@implementer(IQuaiveForm)
class ImportSurvey(EuphorieImportSurvey):
    template = ViewPageTemplateFile("templates/quaive-panel-form.pt")
    label = _("menu_import", default="Import OiRA Tool")
    description = ""
