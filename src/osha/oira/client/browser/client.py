# coding=utf-8
from json import dumps
from plone import api
from Products.Five import BrowserView


class MailingListsJson(BrowserView):
    """Mailing lists (countries, in the future also sectors and tools)"""

    @property
    def results(self):
        """
        List of "mailing list" path/names.

        The format fits pat-autosuggest.
        There is a special label for the "all" list.
        """
        # TODO: require query.
        # q = self.request.get("q", "").strip().lower()
        # if not q:
        #     return []

        catalog = api.portal.get_tool(name="portal_catalog")
        all_users = {"id": "all", "text": "All OiRA users"}
        # if q in all_users["id"] or q in all_users["text"].lower():

        results = [all_users]

        # FIXME: SearchableText="de*" doesn't return Germany
        brains = catalog(
            portal_type="euphorie.clientcountry",
            sort_on="sortable_title",
        )
        results.extend(
            [{"id": brain.getPath(), "text": brain.Title} for brain in brains]
        )
        return results

    def __call__(self):
        """Returns a json meant to be consumed by pat-autosuggest.

        The json lists container that will be used to generate "mailing lists"
        """
        self.request.response.setHeader("Content-type", "application/json")
        return dumps(self.results)
