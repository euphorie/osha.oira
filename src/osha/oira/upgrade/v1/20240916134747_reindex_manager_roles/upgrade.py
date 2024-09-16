from ftw.upgrade import UpgradeStep
from plone import api

import logging


logger = logging.getLogger(__name__)


class ReindexManagerRoles(UpgradeStep):
    """Reindex manager roles."""

    def __call__(self):
        self.install_upgrade_profile()
        sectors = api.portal.get().sectors
        client = api.portal.get().client
        for context in [sectors, client]:
            for brain in api.content.find(context=context, depth=3):
                try:
                    obj = brain.getObject()
                except KeyError:
                    logger.info("Could not get object %s", brain.getPath())
                    continue
                if hasattr(obj, "reindexObject"):
                    obj.reindexObject(idxs=["managerRolesAndUsers"])
