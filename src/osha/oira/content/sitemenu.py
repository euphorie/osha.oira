# coding=utf-8
from Acquisition import aq_inner
from euphorie.deployment.browser import sitemenu
from osha.oira import _
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError


class Sitemenu(sitemenu.Sitemenu):
    @property
    def actions(self):
        """See plonetheme.nuplone.skin.sitemenu.py
        Add extra 'statistics' action.
        """
        menu = super(Sitemenu, self).actions or {}
        children = menu.get("children")
        if not children:
            return None
        submenu = self.statistics()
        if submenu:
            children.append(submenu)
        if children:
            return menu
        else:
            return None

    def statistics(self):
        context = aq_inner(self.context)
        request = self.request
        try:
            # We do a permission check by trying to render the view
            getMultiAdapter((context, request), name="show-statistics")
        except ComponentLookupError:
            return
        menu = {"title": _("menu_admin", default=u"Admin")}
        menu["children"] = [
            {
                "title": _("menu_statistics", default=u"Statistics"),
                "url": "%s/@@show-statistics" % context.absolute_url(),
            }
        ]
        return menu
