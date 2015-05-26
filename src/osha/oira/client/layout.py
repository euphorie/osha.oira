from five import grok
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from zope.interface import Interface

grok.templatedir("templates")

class Shell(grok.View):
    grok.context(Interface)
    grok.name("shell")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("shell")


class Includes(grok.View):
    grok.context(Interface)
    grok.name("includes")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("includes")
