from euphorie.content import MessageFactory as _
from euphorie.content import sector
from five import grok
from osha.oira.interfaces import IOSHAContentSkinLayer
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import dexterity
from plone.directives import form
from z3c.appconfig.interfaces import IAppConfig
from zope import schema
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import logging
import z3c.form

log = logging.getLogger('osha.oira/sector.py')
grok.templatedir("templates")


class IOSHASector(form.Schema):
    """ """
    statistics_level = schema.Choice(
            title=_("label_statistics_level", default=u"Statistics Level"),
            description=_("help_statistics_level",
                default=u"Level 1: Basic statistics about the use of the OiRA "
                        u"tool. Level 2: More detailed statistics regarding "
                        u"the risks"),
            required=True,
            vocabulary=SimpleVocabulary([
                            SimpleTerm(1, title=u"1"),
                            SimpleTerm(2, title=u"2"),
                            ]),
            default=1,
            )

alsoProvides(IOSHASector, IFormFieldProvider)


class OSHASector(MetadataBase):
    statistics_level = DCFieldProperty(IOSHASector['statistics_level'])


class AdminEdit(dexterity.EditForm):
    grok.context(sector.ISector)
    grok.require("cmf.ManagePortal")
    grok.layer(IOSHAContentSkinLayer)
    grok.name("admin-edit")
    grok.template('sector_admin_edit')

    def extractData(self):
        self.fields = self.fields.omit("login", "password")
        if "login" in self.widgets:
            del self.widgets["login"]

        if "password" in self.widgets:
            del self.widgets["password"]
        return super(AdminEdit, self).extractData()


class SectorAdd(dexterity.AddForm):
    grok.context(sector.ISector)
    grok.name('euphorie.sector')
    grok.require("cmf.ModifyPortalContent")
    grok.layer(IOSHAContentSkinLayer)

    def update(self):
        super(SectorAdd, self).update()
        self.widgets['password'].mode = z3c.form.interfaces.HIDDEN_MODE

    def create(self, data):
        content = super(SectorAdd, self).create(data)

        appconfig = getUtility(IAppConfig)
        if not appconfig:
            log.error("Could not get the IAppConfig utility!")
            return content

        settings = appconfig.get('euphorie')
        main_colour = settings.get('main_colour', "#003399")
        support_colour = settings.get('support_colour', "#996699")
        if content.main_colour is None:
            content.main_colour = main_colour

        if content.support_colour is None:
            content.support_colour = support_colour

        return content
