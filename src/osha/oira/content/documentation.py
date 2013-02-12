from five import grok
from euphorie.content.documentation import IDocumentationFolder
from .. import interfaces

grok.templatedir("templates")


class View(grok.View):
    grok.context(IDocumentationFolder)
    grok.require("zope2.View")
    grok.layer(interfaces.IOSHAContentSkinLayer)
    grok.template("documentation_view")
    grok.name("nuplone-view")
