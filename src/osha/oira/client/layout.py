from five import grok
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from zope.interface import Interface

grok.templatedir("templates")


class Shell(grok.View):
    """ Based on the _layouts/shell.html layout in Jekyll. In Plone terms it's
        similar to the main_template.pt.
    """
    grok.context(Interface)
    grok.name("shell")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("shell")


class Includes(grok.View):
    """ This view's templates contains a collection of macros, corresponding to
        the Jekyll includes under the _includes dir.
    """
    grok.context(Interface)
    grok.name("includes")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("includes")
