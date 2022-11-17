# coding=utf-8
from json import dumps
from plone import api
from Products.Five import BrowserView


class MailingListsJson(BrowserView):
    """Mailing lists (countries, in the future also sectors and tools)"""

    def __call__(self):
        """Json list of mailing list ids/names"""
        lists = []
        catalog = api.portal.get_tool(name="portal_catalog")
        self.request.response.setHeader("Content-type", "application/json")
        # TODO: require query.
        # q = self.request.get("q", "").strip().lower()
        # if not q:
        #     return dumps([])

        all_users = {"id": "all", "text": "All OiRA users"}
        # if q in all_users["id"] or q in all_users["text"].lower():
        lists.append(all_users)

        # FIXME: SearchableText="de*" doesn't return Germany
        countries = catalog(portal_type="euphorie.clientcountry")
        lists.extend(
            [{"id": country["id"], "text": country["Title"]} for country in countries]
        )
        # TODO: add sectors and tools

        return dumps(lists)
