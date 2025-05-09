from ftw.upgrade import UpgradeStep
from plone import api


class FixTheDocumentContentType(UpgradeStep):
    """Fix the Document content type."""

    def __call__(self):
        portal_type = "Document"
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.get(portal_type)
        if fti and fti.product == "ATContentTypes":
            portal_types.manage_delObjects([portal_type])
            self.install_upgrade_profile()
