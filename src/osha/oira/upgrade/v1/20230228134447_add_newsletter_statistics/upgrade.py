from ftw.upgrade import UpgradeStep

import logging


logger = logging.getLogger(__name__)


class AddNewsletterStatistics(UpgradeStep):
    """Add newsletter statistics."""

    def __call__(self):
        logger.info(
            "Empty upgrade - statistics database upgrades are now handled in "
            "oira.statistics.deployment"
        )
