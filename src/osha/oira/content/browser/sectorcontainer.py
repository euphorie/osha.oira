from Acquisition import aq_inner
from euphorie.content.browser.library import get_library
from euphorie.content.utils import summarizeCountries
from Products.Five import BrowserView


class SectorContainerView(BrowserView):
    @property
    def countries(self):
        return summarizeCountries(aq_inner(self.context), self.request)

    @property
    def library_info(self):
        library = get_library(self.context)
        return [dict(title=lib["title"], url=lib["url"]) for lib in library]
