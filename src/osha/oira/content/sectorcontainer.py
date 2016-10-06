from Acquisition import aq_inner
from five import grok
from euphorie.content import sectorcontainer
from euphorie.content.utils import summarizeCountries
from euphorie.content.library import get_library
from ..interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class View(sectorcontainer.View):
    grok.context(sectorcontainer.ISectorContainer)
    grok.require("zope2.View")
    grok.layer(IOSHAContentSkinLayer)
    grok.template("sectorcontainer_view")
    grok.name("nuplone-view")

    def update(self):
        self.countries = summarizeCountries(
            aq_inner(self.context), self.request)
        library = get_library(self.context)
        self.library_info = [
            dict(title=lib['title'], url=lib['url']) for lib in library]
