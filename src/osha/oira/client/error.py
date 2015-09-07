from euphorie.client.error import ErrorView
from five import grok
import zExceptions
from .interfaces import IOSHAClientSkinLayer

grok.templatedir("templates")


class OSHAErrorView(ErrorView):
    grok.layer(IOSHAClientSkinLayer)
    grok.name("index.html")
    grok.template("error")


class OSHANotFound(OSHAErrorView):
    grok.context(zExceptions.NotFound)
    grok.template("error_notfound")
