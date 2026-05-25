from euphorie.content.browser.risk import RiskView
from euphorie.content.solution import ISolution
from euphorie.content.survey import get_tool_type
from euphorie.content.utils import IToolTypesInfo
from euphorie.content.utils import ToolTypesInfo
from logging import getLogger
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.namedfile.scaling import ImageScaling
from plone.supermodel.model import SchemaClass
from Products.CMFCore.permissions import AddPortalContent
from Products.Five import BrowserView
from zope.component import getUtility
from zope.interface import providedBy


logger = getLogger(__name__)

try:
    # This imports a private function, so let's catch an ImportError.
    from plone.app.content.browser.folderfactories import _allowedTypes
except ImportError:
    logger.warning(
        "Import of private function failed: "
        "plone.app.content.browser.folderfactories._allowedTypes"
    )
    _allowedTypes = None


class QuaiveHelpers(BrowserView):

    @property
    @memoize
    def can_add(self):
        """Can the user add content here?

        The user must have the 'Add portal content' permission.
        And at least one content type must be addable on the context.
        Otherwise there is no need to show an Add menu.

        The code for checking if types can be added, is adapted from
        the plone_contentmenu_factory in plone.app.contentmenu.
        """
        context = self.context
        if not api.user.has_permission(AddPortalContent, obj=context):
            return False
        # First check if we are folderish, otherwise
        # context.allowedContentTypes will be inherited from our parent.
        context_state = api.content.get_view(
            "plone_context_state",
            context,
            self.request,
        )
        if not context_state.is_structural_folder():
            return False
        if _allowedTypes is None:
            return bool(context.allowedContentTypes())
        # This does the same as the previous line, except that it is
        # cached on the request.
        return bool(_allowedTypes(self.request, context))

    @property
    @memoize
    def has_contents(self):
        context_state = api.content.get_view(
            "plone_context_state",
            self.context,
            self.request,
        )
        if not context_state.is_structural_folder():
            return False
        return bool(self.context.contentIds())


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

    image_scale_options = {
        "scale": "training",
        "pre": True,
    }

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

    def get_scale_url(self, context, image_field: str) -> str:
        """Return the scale to use for the given image field."""
        images_view: ImageScaling = api.content.get_view(
            name="images", context=context, request=self.request
        )  # type: ignore
        return images_view.scale(image_field, **self.image_scale_options).url

    @property
    def legacy_information_scales_and_captions(self) -> list[dict]:
        """Return the images that should go in the information content well
        coming from the legacy fields:

        1. image and image_caption
        2. image2 and caption2
        3. image3 and caption3
        4. image4 and caption4
        """
        legacy_fields = [
            ("image", "image_caption"),
            ("image2", "caption2"),
            ("image3", "caption3"),
            ("image4", "caption4"),
        ]
        scales_and_captions = []
        for image_field, caption_field in legacy_fields:
            image = getattr(self.context, image_field, None)
            caption = getattr(self.context, caption_field, None)
            if image:
                scale = {
                    "url": self.get_scale_url(self.context, image_field),
                    "caption": caption or None,
                }
                scales_and_captions.append(scale)
        return scales_and_captions

    @property
    def information_scales_and_captions(self):
        """Return the images that should go in the information content well.

        Returns a list of dicts with a scale URL and a title.
        """
        scales_and_captions = []

        # Add images stored in legacy fields that will be removed one day
        scales_and_captions.extend(self.legacy_information_scales_and_captions)

        # The modern and preferred approach is to use
        # a list field with captioned images.
        related_images = self.context.related_images or []
        for relation in related_images:
            image = relation.image.to_object
            if image:
                scale = {
                    "url": self.get_scale_url(image, "image"),
                    "caption": relation.caption or None,
                }
                scales_and_captions.append(scale)

        return scales_and_captions
