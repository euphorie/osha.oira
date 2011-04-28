from five import grok
from euphorie.content import profilequestion

grok.templatedir("templates")

class View(profilequestion.View):
    """ Override so that we can use our own template
    """
    grok.template("profilequestion_view")
