from logging import getLogger
from plone.supermodel.model import SchemaClass
from Products.Five import BrowserView
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
