from five import grok
from euphorie.client import login
from osha.oira.interfaces import IOSHAClientSkinLayer

grok.templatedir("templates")

class Register(login.Register):
    grok.require("zope2.View")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("register")
