# coding=utf-8
import logging
from zope.interface import Interface
from five import grok
from .interfaces import IOSHAClientSkinLayer

log = logging.getLogger(__name__)
grok.templatedir("templates")


class Disclaimer(grok.View):
    grok.context(Interface)
    grok.layer(IOSHAClientSkinLayer)
    grok.name("disclaimer")
    grok.require("zope2.View")
    grok.template("disclaimer")
