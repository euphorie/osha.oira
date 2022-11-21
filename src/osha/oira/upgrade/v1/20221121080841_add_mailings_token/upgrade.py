from ftw.upgrade import UpgradeStep
from plone import api
from uuid import uuid4


class AddMailingsToken(UpgradeStep):
    """Add mailings token."""

    def __call__(self):
        self.install_upgrade_profile()
        api.portal.set_registry_record("osha.oira.mailings.token", uuid4().hex)
