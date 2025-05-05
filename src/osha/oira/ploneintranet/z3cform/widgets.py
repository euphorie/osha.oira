from plone import api
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IMultiWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import MultiWidget
from zope.interface import implementer
from zope.interface import implementer_only


class IRelatedImagesWidget(IMultiWidget):
    """Marker interface for the related images widget."""


@implementer_only(IRelatedImagesWidget)
class RelatedImagesWidget(MultiWidget):
    """We need to override the MultiWidget class to have our own extract method
    that sorts the values based on a custom request parameter.

    It also has some helpers to render some widget elements.
    """

    def get_image_tag(self, idx):
        """Return the HTML tag for the image at the given index."""
        try:
            related_image = self.context.related_images[idx]
        except IndexError:
            return ""

        try:
            # Get the image object from the relation
            image = related_image.image.to_object
        except AttributeError:
            # If the image is not found, return an empty string
            return ""

        if not image:
            # If the image is None, return an empty string
            return ""

        images_view = api.content.get_view(
            name="images", context=image, request=self.request
        )
        return images_view.tag(scale="mini", css_class="thumbnail")

    def sort_values(self, values: list):
        """Sort the values based on the position in the request.

        This happens when the user drags and drops the captioned images in the widget.

        positions can be None, '0', or ['0', '1', ...]
        """
        positions = self.request.form.get(f"{self.name}-position")
        if not positions:
            return values

        # This will work if positions is a string or a list of strings,
        # assuming the strings are convertible to integers
        try:
            positions = list(map(int, positions))
        except ValueError:
            return values

        # Complete the positions list with all the missing indexes from the values
        for i in range(len(values)):
            if i not in positions:
                positions.append(i)

        sorted_values = [
            values[position] for position in positions if position < len(values)
        ]
        return sorted_values

    def extract(self) -> list:
        """Extract the value from the widget"""
        value = super().extract()
        return self.sort_values(value)


@implementer(IFieldWidget)
def RelatedImagesFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, RelatedImagesWidget(request))
