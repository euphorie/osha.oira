from functools import cached_property
from osha.oira import _
from osha.oira.behaviors.related_images import ImageWithCaption
from osha.oira.ploneintranet.interfaces import IQuaiveForm
from plone import api
from plone.autoform.form import AutoExtensibleForm
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain
from z3c.form import form
from zope import schema
from zope.interface import implementer
from zope.interface import Interface


class IImageBank(Interface):
    """This schema is used to select the images to be used in the image bank by UID."""

    uids = schema.List(
        title=_("Image UIDs"),
        description=_("List of image UIDs"),
        value_type=schema.TextLine(
            title=_("Image UID"),
            description=_("UID of the image"),
        ),
        required=False,
    )


@implementer(IQuaiveForm)
class ImageBankPanel(AutoExtensibleForm, form.Form):
    """Update the company details.

    View name: @@panel-select-image-image-bank
    """

    schema = IImageBank
    ignoreContext = True
    oira_type = ""

    @cached_property
    def template(self):
        return self.index

    @property
    def available_images(self):
        """Return the available images from the catalog"""
        brains = api.content.find(
            portal_type="Image",
            sort_on="sortable_title",
        )
        return brains

    def get_image_scale(self, image: AbstractCatalogBrain) -> str:
        """Return the image scale URL."""
        try:
            scale_path = image.image_scales["image"][0]["scales"]["mini"]["download"]
        except (KeyError, IndexError):
            # Handle the case where the scale is not available
            return ""

        return f"{image.getURL()}/{scale_path}"

    def redirect(self):
        """Redirect to the edit form."""
        self.request.response.redirect(f"{self.context.absolute_url()}/@@quaive-edit")

    @property
    def existing_relations(self):
        """Return a mapping with the existing valid relations grouped by UID."""
        related_images = self.context.related_images or []
        mapping = {}
        for relation in related_images:
            try:
                image = relation.image.to_object
            except AttributeError:
                image = None
            if image:
                mapping[image.UID()] = relation
        return mapping

    def set_relations(self, data):
        """Set the relations based on the selected images."""
        existing_relations = self.existing_relations
        new_relations = []

        # Transform the user input in to a list of relations
        uids = data.get("uids", []) or []
        for uid in uids:
            if not uid or uid in existing_relations:
                # This disallows duplicates
                continue

            image = api.content.get(UID=uid)
            if image:
                new_relations.append(ImageWithCaption.from_uid(uid))

        if new_relations:
            update_relations = self.context.related_images or []
            update_relations.extend(new_relations)

            # This ensures the object is marked as changed
            self.context.related_images = update_relations

    @form.button.buttonAndHandler(_("Insert"), name="insert")
    def handle_insert(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
        else:
            self.set_relations(data)
        self.redirect()

    @form.button.buttonAndHandler(_("Cancel"), name="cancel")
    def handle_cancel(self, action):
        """Cancel button"""
        self.redirect()

    def updateActions(self):
        super().updateActions()
        for action in self.actions.values():
            action.addClass("close-panel")
        self.actions["insert"].addClass("btn-primary")
