from ftw.upgrade import UpgradeStep
from osha.oira.upgrade.utils import alembic_upgrade_to


class AddNewsletterSettings(UpgradeStep):
    """Add newsletter settings."""

    def __call__(self):
        alembic_upgrade_to(self.target_version)
