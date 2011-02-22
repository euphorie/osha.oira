from five import grok
from euphorie.client import risk
import interfaces

grok.templatedir("templates")

class OSHAIdentificationView(risk.IdentificationView):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("risk_identification")
