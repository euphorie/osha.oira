from ftw.upgrade import UpgradeStep
from osha.oira.upgrade.utils import alembic_upgrade_statistics_to


class AddNewsletterStatistics(UpgradeStep):
    """Add newsletter statistics."""

    def __call__(self):
        alembic_upgrade_statistics_to(self.target_version)
