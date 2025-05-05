from euphorie.content import MessageFactory as _
from plone import api
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form.interfaces import IEditForm
from z3c.form.object import registerFactoryAdapter
from z3c.relationfield import RelationValue
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IList


class IImageWithCaption(Interface):
    """Interface for the value that will store the relation to the image
    and the caption.
    """

    image = RelationChoice(
        title=_("Related image"),
        source=CatalogSource(portal_type="Image"),
        required=False,
    )

    caption = schema.Text(
        title=_("Image caption"),
        description=_("Write a caption for this image. (Optional)"),
        required=False,
    )


@implementer(IImageWithCaption)
class ImageWithCaption:
    """A class that stores a relation to an image and an optional caption."""

    def __init__(self, image=None, caption=None):
        self.image = image
        self.caption = caption

    @classmethod
    def from_uid(cls, uid):
        """Helper to initialize this class from an object uid"""
        image = api.content.get(UID=uid)
        intids = getUtility(IIntIds)
        return cls(RelationValue(intids.getId(image)), "")


registerFactoryAdapter(IImageWithCaption, ImageWithCaption)


class IRelatedImagesField(IList):
    """A field that allows to edit a list of ImageWithCaption instances"""


@implementer(IRelatedImagesField)
class RelatedImagesField(schema.List):
    """A field that allows to edit a list of ImageWithCaption instances"""

    def __init__(self, **kwargs):
        if "value_type" in kwargs:
            raise ValueError("value_type must not be set")

        super().__init__(
            value_type=schema.Object(
                schema=IImageWithCaption, title=_("Related image with caption")
            ),
            **kwargs
        )


@provider(IFormFieldProvider)
class IRelatedImagesBehavior(model.Schema):
    """A behavior that adds to a dexterity object a related_images field
    used to store a list of images with captions.
    """

    related_images = RelatedImagesField(
        title=_(
            "Add an image gallery by uploading "
            "a set of images or by selecting them from Image bank."
        ),
        description=_("List of related images with captions."),
        required=False,
    )
    model.fieldset(
        "information",
        label=_("Information"),
        fields=["related_images"],
    )
    directives.omitted("related_images")
    directives.no_omit(IEditForm, "related_images")
