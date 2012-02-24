from five import grok
from euphorie.client import login as register
from plonetheme.nuplone.skin import login
from osha.oira.interfaces import IOSHAClientSkinLayer
from osha.oira.interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")

class Register(register.Register):
    grok.require("zope2.View")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("register")

class Login(login.Login):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("login")
