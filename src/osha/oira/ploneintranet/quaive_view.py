from euphorie.content.browser.risk import RiskView
from euphorie.content.solution import ISolution
from euphorie.content.survey import get_tool_type
from euphorie.content.utils import IToolTypesInfo
from euphorie.content.utils import ToolTypesInfo
from logging import getLogger
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.supermodel.model import SchemaClass
from Products.Five import BrowserView
from zope.component import getUtility
from zope.interface import providedBy


logger = getLogger(__name__)


class BaseQuaiveView(BrowserView):
    """Base class for Quaive views

    By default serve the nuplone-view, which is the expected base view
    for the object.

    We anyway want to have dedicated views for all the content types, so we log
    a warning if a more specific view is not available.

    If you see the warning, you need to implement a more specific quaive-view
    for that content type.
    """

    def __call__(self) -> str:

        schema = next(
            (
                iface
                for iface in providedBy(self.context)
                if isinstance(iface, SchemaClass)
            ),
            None,
        )
        logger.warning(
            "No specific @@quaive-view found for %r (schema=%r), please register one",
            self.context.portal_type,
            schema,
        )
        return self.context.restrictedTraverse("@@nuplone-view")().replace(
            'id="mainContent"', 'id="quaive-content"'
        )


class QuaiveRiskView(RiskView):

    @property
    def tool_type(self):
        return get_tool_type(self.my_context)

    @property
    @memoize_contextless
    def tti(self) -> ToolTypesInfo:
        return getUtility(IToolTypesInfo)

    @property
    @memoize
    def use_existing_measures(self) -> bool:
        return (
            api.portal.get_registry_record(
                "euphorie.use_existing_measures", default=False
            )
            and self.tool_type in self.tti.types_existing_measures
        )

    @property
    def show_existing_measures(self):
        """Override the default behaviour to show existing measures"""
        if not self.use_existing_measures:
            return False

        return True

    @property
    def solutions(self):
        return [
            solution
            for solution in self.my_context.values()
            if ISolution.providedBy(solution)
        ]
