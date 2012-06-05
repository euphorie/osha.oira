from five import grok
from zope.site.hooks import getSite
from Acquisition import aq_parent

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.kss.plonekssview import PloneKSSView

from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from plonetheme.nuplone.skin import actions
from plonetheme.nuplone.utils import getPortal
from euphorie.content import MessageFactory as _
from euphorie.content import surveygroup
from euphorie.content.survey import ISurvey

grok.templatedir("templates")


class View(surveygroup.View):
    grok.layer(NuPloneSkin)
    grok.name("nuplone-view")
    grok.template("surveygroup_view")
    
    def surveys(self):
        templates = [ dict(title=survey.title, url=survey.absolute_url())
                      for survey in self.context.values()
                      if ISurvey.providedBy(survey)
                    ]
        return templates

View.render = None


class AddForm(surveygroup.AddForm, PloneKSSView):
    """ """
    grok.context(surveygroup.ISurveyGroup)
    grok.name("euphorie.surveygroup")
    grok.require("euphorie.content.AddNewRIEContent")
    template = ViewPageTemplateFile("templates/surveygroup_add.pt")

    def createAndAdd(self, data):
        """ #3036: Set a 'default' value on the Survey that was newly created in the
            SurveyGroup.
        """
        obj = super(AddForm, self).createAndAdd(data)
        try:
            surveys = obj.objectValues("Dexterity Container")
        except IndexError:
            return obj

        macro = getSite().unrestrictedTraverse('default_introduction')()
        for survey in surveys:
            survey.introduction = macro
            survey.reindexObject()
        return obj


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


