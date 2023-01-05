from AccessControl import Unauthorized
from Acquisition import aq_inner
from euphorie.deployment.browser import sitemenu
from osha.oira import _


class Sitemenu(sitemenu.Sitemenu):
    @property
    def actions(self):
        """See plonetheme.nuplone.skin.sitemenu.py Add extra 'statistics'
        action."""
        menu = super().actions or {}
        children = menu.get("children")
        if not children:
            return None
        submenu = self.statistics()
        if submenu:
            self.add_submenu(children, submenu)
        if children:
            return menu
        else:
            return None

    def statistics(self):
        context = aq_inner(self.context)

        # We try to traverse to the view. It would fail for the wrong context
        # or if permissions are not met.
        try:
            self.context.restrictedTraverse("@@show-statistics")
        except (AttributeError, Unauthorized):
            return None

        menu = {"title": _("menu_admin", default="Admin")}
        menu["children"] = [
            {
                "title": _("menu_statistics", default="Statistics"),
                "url": "%s/@@show-statistics" % context.absolute_url(),
            }
        ]
        return menu
