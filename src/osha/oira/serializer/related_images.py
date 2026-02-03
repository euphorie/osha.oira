from osha.oira.behaviors.related_images import IRelatedImagesField
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(IRelatedImagesField, IDexterityContent, Interface)
@implementer(IFieldSerializer)
class RelatedImagesFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        """Serializer to allow this field to be serialized by Plone.restapi"""
        value = self.get_value() or []
        items = []

        for item in value:
            image = getattr(item, "image", None)
            caption = getattr(item, "caption", None)
            items.append(
                {
                    "image": json_compatible(image),
                    "caption": json_compatible(caption),
                }
            )

        return json_compatible(items)
