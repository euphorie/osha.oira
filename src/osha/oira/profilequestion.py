from five import grok
from euphorie.content import profilequestion
from .interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class View(profilequestion.View):
    """ Override so that we can use our own template
    """
    grok.template("profilequestion_view")
    grok.layer(IOSHAContentSkinLayer)
