from euphorie.client.help import HelpView
from five import grok
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from zope.interface import Interface

grok.templatedir("templates")


class Plain(grok.View):
    """ Based on the shell template, but stripped down to a minimum (no
        sidebar, no header). Meant for use in things like pdf reports.
    """
    grok.context(Interface)
    grok.name("plain")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("plain")


class Tooltips(grok.View):
    """ This view's templates contains a number of <div> element that are used
    for various tooltips.
    In proto, see explanations.html

    """
    grok.context(Interface)
    grok.name("tooltips")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("tooltips")


class OSHAHelpView(HelpView):
    grok.layer(IOSHAClientSkinLayer)
    grok.name("help")
    grok.template("help")
