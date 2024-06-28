from ftw.upgrade import UpgradeStep

import logging


logger = logging.getLogger(__name__)


class InitializeStatisticsForSlovakia(UpgradeStep):
    """Initialize statistics for Slovakia."""

    def __call__(self):
        logger.info(
            "Empty upgrade - statistics database upgrades are now handled in "
            "oira.statistics.deployment"
        )
