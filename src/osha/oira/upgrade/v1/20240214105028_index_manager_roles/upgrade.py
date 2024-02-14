from ftw.upgrade import UpgradeStep
from plone import api


class IndexManagerRoles(UpgradeStep):
    """Index manager roles."""

    def __call__(self):
        self.install_upgrade_profile()
        client = api.portal.get().client
        for brain in api.content.find(context=client, depth=3):
            brain.getObject().reindexObject(idxs=["managerRolesAndUsers"])
