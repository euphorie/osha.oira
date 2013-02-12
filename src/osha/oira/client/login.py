from five import grok
from euphorie.client import login as register
from .interfaces import IOSHAClientSkinLayer

grok.templatedir("templates")


class Register(register.Register):
    grok.require("zope2.View")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("register")
