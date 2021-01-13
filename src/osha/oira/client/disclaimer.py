# coding=utf-8
from .interfaces import IOSHAClientSkinLayer
from five import grok
from zope.interface import Interface

import logging


log = logging.getLogger(__name__)
grok.templatedir("templates")


class Disclaimer(grok.View):
    grok.context(Interface)
    grok.layer(IOSHAClientSkinLayer)
    grok.name("disclaimer")
    grok.require("zope2.View")
    grok.template("disclaimer")
