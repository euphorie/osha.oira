from five import grok
from zope import schema
from zope.interface import implements

from plone.directives import form
from plone.directives import dexterity
from plone.app.dexterity.behaviors.metadata import IBasic

from euphorie.content import MessageFactory as _

from osha.oira.interfaces import IOSHAContentSkinLayer
from osha.oira.z3cform.widget import LargeTextAreaFieldWidget

grok.templatedir("templates")

class IHomePage(form.Schema, IBasic):
    """ Custom user editable homepage
    """
    description = schema.Text(
        title = _("label_module_description", u"HTML Source Code"))
    form.widget(description=LargeTextAreaFieldWidget)


class HomePage(dexterity.Container):
    implements(IHomePage)


class View(grok.View):
    grok.context(IHomePage)
    grok.require("zope2.View")
    grok.layer(IOSHAContentSkinLayer)
    grok.name("oira-homepage")
    grok.template("custom_homepage")

    def render_body(self):
        return self.context.description

