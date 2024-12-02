from ftw.upgrade import UpgradeStep
from plone import api


class FixTheFolderContentType(UpgradeStep):
    """Fix the Folder content type."""

    def __call__(self):
        portal_type = "Folder"
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.get(portal_type)
        if fti and fti.product == "plone.app.folder":
            portal_types.manage_delObjects([portal_type])
            self.install_upgrade_profile()
