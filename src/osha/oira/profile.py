from five import grok
from euphorie.client import profile
from osha.oira import interfaces

grok.templatedir("templates")

class OSHAProfile(profile.Profile):
    """ Override the original profile to provide our own template.
    """
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.template("profile")
    grok.name("profile")

