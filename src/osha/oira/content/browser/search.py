from euphorie.deployment.browser.search import ContextSearch
from euphorie.deployment.browser.search import SEARCHED_TYPES
from euphorie.deployment.browser.search import TYPES_MAP
from plone import api
from plone.base.utils import safe_text
from plone.memoize.view import memoize


class OshaContextSearch(ContextSearch):
    @property
    @memoize
    def portal_path_len(self):
        return len("/".join(api.portal.get().getPhysicalPath()))

    @property
    @memoize
    def results(self):
        qs = self.request.form.get("q", None)
        if not qs:
            return

        qs = f'"{safe_text(qs)}*"'
        path = "/".join(self.context.getPhysicalPath())
        query = {"SearchableText": qs, "portal_type": SEARCHED_TYPES, "path": path}

        ct = api.portal.get_tool("portal_catalog")
        brains = ct.searchResults(**query)
        return [
            {
                "url": brain.getURL(),
                "title": brain.Title,
                "typ": TYPES_MAP.get(brain.portal_type, "unknown"),
                "path": brain.getPath()[self.portal_path_len :],
                "description": brain.Description,
            }
            for brain in brains
        ]
