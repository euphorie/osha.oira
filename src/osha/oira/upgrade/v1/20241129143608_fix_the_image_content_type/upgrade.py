from ftw.upgrade import UpgradeStep
from plone import api


class FixTheImageContentType(UpgradeStep):
    """Fix the Image content type."""

    def __call__(self):
        portal_type = "Image"
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.get(portal_type)
        if fti and fti.product == "plone.app.blob":
            portal_types.manage_delObjects([portal_type])
            self.install_upgrade_profile()
