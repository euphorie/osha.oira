from five import grok
from Acquisition import aq_parent
from Products.statusmessages.interfaces import IStatusMessage
from plonetheme.nuplone.skin import actions
from plonetheme.nuplone.utils import getPortal
from euphorie.content import MessageFactory as _
from euphorie.content import surveygroup


class Delete(actions.Delete):
    """ Only delete the surveygroup if it doesn't have a published version.
    """
    grok.context(surveygroup.ISurveyGroup)

    def verify(self, container, context):
        flash = IStatusMessage(self.request).addStatusMessage
        surveygroup = context
        sector = container
        country = aq_parent(sector)
        client = getPortal(container).client

        if country.id not in client:
            return True

        cl_country = client[country.id]
        if sector.id not in cl_country:
            return True

        cl_sector = cl_country[sector.id]
        if surveygroup.id not in cl_sector:
            return True

        surveys = [s for s in cl_sector[surveygroup.id].values() if s.id != 'preview']
        if surveys:
            flash(
                _("message_not_delete_published_surveygroup",
                default=u"You can not delete an OiRA tool that has been published."),
                "error"
                )
            self.request.response.redirect(context.absolute_url())
            return False
        return True
