from ftw.upgrade import UpgradeStep
from logging import getLogger
from plone import api


logger = getLogger(__name__)


class RemoveUnusedBehavior(UpgradeStep):
    """Remove unused behavior."""

    def __call__(self):
        """Remove from the euphorie.sector
        fti the behavior osha.oira.sector.IOSHASector
        """
        portal_types = api.portal.get_tool("portal_types")
        fti = portal_types.get("euphorie.sector")
        if fti and "osha.oira.sector.IOSHASector" in fti.behaviors:
            fti.behaviors = tuple(
                [
                    behavior
                    for behavior in fti.behaviors
                    if behavior != "osha.oira.sector.IOSHASector"
                ]
            )
            logger.info(
                "Removed behavior osha.oira.sector.IOSHASector from euphorie.sector"
            )
        else:
            logger.info(
                "Behavior osha.oira.sector.IOSHASector not found in euphorie.sector"
            )
