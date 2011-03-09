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

    def updateActions(self):
        if self.fields['main_colour'].field.get(self.context) is None or \
           self.fields['support_colour'].field.get(self.context) is None:

            appconfig = getUtility(IAppConfig)
            settings = appconfig.get('euphorie')
            main_colour  = settings.get('main_colour', "#031c48")
            support_colour  = settings.get('support_colour', "#996699")

            if self.fields['main_colour'].field.get(self.context) is None:
                self.fields['main_colour'].field.set(self.context, main_colour)

            if self.fields['support_colour'].field.get(self.context) is None:
                self.fields['support_colour'].field.set(self.context, support_colour)

        self.fields['main_colour'].field.required = True
        self.fields['support_colour'].field.required = True
        return super(Settings, self).updateActions()


class SectorAdd(dexterity.AddForm):
    grok.context(sector.ISector)
    grok.name('euphorie.sector')
    grok.require("cmf.ModifyPortalContent")
    grok.layer(NuPloneSkin)

    def updateActions(self):
        appconfig = getUtility(IAppConfig)
        settings = appconfig.get('euphorie')
        main_colour  = settings.get('main_colour', "#031c48")
        support_colour  = settings.get('support_colour', "#996699")

        self.fields['main_colour'].field.default = main_colour
        self.fields['main_colour'].field.required = True

        self.fields['support_colour'].field.default = support_colour
        self.fields['support_colour'].field.required = True
        return super(SectorAdd, self).updateActions()

