from ftw.upgrade import UpgradeStep
from logging import getLogger
from plone import api


logger = getLogger("__name__")


class RemoveTheATContentTypes(UpgradeStep):
    """Remove the AT content types."""

    def __call__(self):
        portal_types = api.portal.get_tool("portal_types")
        for portal_type in [
            "ATBooleanCriterion",
            "ATCurrentAuthorCriterion",
            "ATDateCriteria",
            "ATDateRangeCriterion",
            "ATListCriterion",
            "ATPathCriterion",
            "ATRelativePathCriterion",
            "ATPortalTypeCriterion",
            "ATReferenceCriterion",
            "ATSelectionCriterion",
            "ATSimpleIntCriterion",
            "ATSimpleStringCriterion",
            "ATSortCriterion",
            "Topic",
        ]:
            if portal_type in portal_types:
                logger.info("Removing %r", portal_type)
                portal_types.manage_delObjects(portal_type)
