from ftw.upgrade import UpgradeStep
from plone import api


class FixTheFileContentType(UpgradeStep):
    """Fix the File content type."""

    def __call__(self):
        portal_type = "File"
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.get(portal_type)
        if fti and fti.product == "plone.app.blob":
            portal_types.manage_delObjects([portal_type])
            self.install_upgrade_profile()
