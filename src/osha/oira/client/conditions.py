# coding=utf-8
from five import grok
from euphorie.client.conditions import TermsAndConditions as BaseTermsAndConditions  # noqa
from .interfaces import IOSHAClientSkinLayer

grok.templatedir("templates")


class TermsAndConditions(BaseTermsAndConditions):
    grok.name("terms-and-conditions")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("conditions")
