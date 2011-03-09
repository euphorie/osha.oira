from five import grok
from zope.component import getUtility
from z3c.appconfig.interfaces import IAppConfig
from euphorie.content import sector
from plone.directives import dexterity
from plonetheme.nuplone.skin.interfaces import NuPloneSkin

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

