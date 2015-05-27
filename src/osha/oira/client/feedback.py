from zope.interface import Interface
from five import grok
from osha.oira.client.interfaces import IOSHAClientSkinLayer

grok.templatedir("templates")


class UserMenu(grok.View):
    grok.context(Interface)
    grok.name("user-menu.html")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("user-menu")
