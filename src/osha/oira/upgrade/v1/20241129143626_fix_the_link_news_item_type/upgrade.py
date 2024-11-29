from ftw.upgrade import UpgradeStep
from plone import api


class FixTheLinkNewsItemType(UpgradeStep):
    """Fix the Link News Item type."""

    def __call__(self):
        portal_type = "News Item"
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.get(portal_type)
        if fti and fti.product == "ATContentTypes":
            portal_types.manage_delObjects([portal_type])
            self.install_upgrade_profile()
