from plone.directives import dexterity
from euphorie.content.countrymanager import ICountryManager
from five import grok
from osha.oira.interfaces import IOSHAContentSkinLayer
import z3c.form


class AddForm(dexterity.AddForm):
    grok.context(ICountryManager)
    grok.require("cmf.AddPortalContent")
    grok.layer(IOSHAContentSkinLayer)
    grok.name("euphorie.countrymanager")

    def update(self):
        super(AddForm, self).update()
        self.widgets['password'].mode = z3c.form.interfaces.HIDDEN_MODE
