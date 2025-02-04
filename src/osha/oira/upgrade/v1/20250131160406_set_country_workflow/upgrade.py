from ftw.upgrade import UpgradeStep
from plone import api


class SetCountryWorkflow(UpgradeStep):
    """Set country workflow."""

    def __call__(self):
        self.install_upgrade_profile()
        for brain in api.content.find(portal_type="euphorie.country"):
            obj = brain.getObject()
            obj.reindexObject(idxs=["review_state"])
