# -*- coding: utf-8 -*-
from ..interfaces import IOSHAContentSkinLayer
from five import grok
from plone.app.controlpanel.site import ISiteSchema
from plonetheme.nuplone.skin import layout as nuplone
from zope.component.hooks import getSite
from zope.interface import Interface

grok.templatedir("templates")


class Layout(nuplone.Layout):
    grok.context(Interface)
    grok.name("layout")
    grok.layer(IOSHAContentSkinLayer)
    grok.template("layout")

    def get_webstats_js(self):
        site = getSite()
        return ISiteSchema(site).webstats_js
