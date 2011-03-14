from five import grok
from Acquisition import aq_parent
from zope.component import getUtility
from z3c.appconfig.interfaces import IAppConfig
from plone.directives import dexterity
from Products.statusmessages.interfaces import IStatusMessage
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from plonetheme.nuplone.skin import actions
from plonetheme.nuplone.utils import getPortal
from euphorie.content import sector
from euphorie.content import MessageFactory as _
from euphorie.content.survey import ISurvey

grok.templatedir("templates")

class Settings(sector.Settings):
    """ Override so that we can use our own template
    """ 
    grok.template("settings")

class SectorAdd(dexterity.AddForm):
    grok.context(sector.ISector)
    grok.name('euphorie.sector')
    grok.require("cmf.ModifyPortalContent")
    grok.layer(NuPloneSkin)

    def create(self, data):
        content = super(SectorAdd, self).create(data)

        appconfig = getUtility(IAppConfig)
        settings = appconfig.get('euphorie')
        main_colour  = settings.get('main_colour', "#031c48")
        support_colour  = settings.get('support_colour', "#996699")
        if content.main_colour is None:
            content.main_colour = main_colour

        if content.support_colour is None:
            content.support_colour = support_colour
            
        return content

class View(sector.View):
    grok.template("sector_view")
    grok.name("nuplone-view")


class Delete(actions.Delete):
    """ Only delete the sector if it doesn't have any published surveys.
    """
    grok.context(sector.ISector)

    def verify(self, container, context):
        flash = IStatusMessage(self.request).addStatusMessage
        sector = context
        country = container
        client = getPortal(container).client

        if country.id not in client:
            return True

        cl_country = client[country.id]
        if sector.id not in cl_country:
            return True

        # Look for any published surveys in the client sector, and prevent
        # deletion if any are found
        cl_sector = cl_country[sector.id]
        surveys = [s for s in cl_sector.values() if s.id != 'preview']
        if surveys:
            flash(
                _("message_not_delete_published_sector", 
                default=u"You can not delete a sector that contains published OiRA tools."), 
                "error"
                )
            self.request.response.redirect(context.absolute_url())
            return False
        return True



