from five import grok
from euphorie.client.country import View as EuphorieView
from osha.oira.interfaces import IOSHAClientSkinLayer

grok.templatedir("templates")

class View(EuphorieView):
    grok.layer(IOSHAClientSkinLayer)
    grok.template("sessions")

