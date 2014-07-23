from five import grok
from plonetheme.nuplone.skin import login
from zope.interface import Interface
from osha.oira.interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class Login(login.Login):
    """ Override so that we can have our own template.
    """
    grok.context(Interface)
    grok.layer(IOSHAContentSkinLayer)
    grok.name("login")
    grok.template("login")
