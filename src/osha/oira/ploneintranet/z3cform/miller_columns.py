from Acquisition import aq_chain
from Acquisition import aq_inner
from euphorie.content.sectorcontainer import ISectorContainer
from functools import cached_property
from osha.oira.interfaces import IOSHAContentSkinLayer
from plone import api
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.interfaces import IContentBrowserWidget
from plone.app.z3cform.widgets.contentbrowser import ContentBrowserWidget
from plone.restapi.serializer.utils import get_portal_type_title
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IChoice

import logging


logger = logging.getLogger(__name__)


class IPIContentBrowserWidget(IContentBrowserWidget):
    """Marker interface for a custom content browser widget"""


@implementer_only(IPIContentBrowserWidget)
class PIContentBrowserWidget(ContentBrowserWidget):

    @cached_property
    def widget_url(self):
        """Get the URL of the widget that uses this panel."""
        current_url = self.request.getURL().partition("++widget++")[0]
        return f"{current_url}/++widget++{self.name}"

    @property
    def query(self):
        if self.field is None:
            # Not yet initialized.
            return {}
        return self.field.source.query or {}

    @cached_property
    def actual_context(self):
        """Return the actual content item."""
        return self.form.getContent()

    @cached_property
    def start_object(self):
        """Return the object to start browsing at."""
        for obj in aq_chain(aq_inner(self.actual_context)):
            if ISectorContainer.providedBy(obj):
                return obj

    @cached_property
    def source_object(self):
        """Get the currently selected source object.

        This can be a folder where we browse for other items.
        Or it can be an item that we have selected for previewing.
        """
        uid = self.request.form.get("next_container_uid") or self.request.form.get(
            self.name
        )
        if uid:
            return api.content.get(UID=uid)
        return self.start_object or self.actual_context

    @cached_property
    def results(self):
        """List of items to show in one Miller column.

        These are all browsable content items directly within the source object.
        We return a list of tuples: (brain, selectable yes/no).
        """
        # First get all folderish items.
        folders = api.content.find(
            context=self.source_object, is_folderish=True, depth=1
        )

        # Then get all selectable items.  The results may overlap with the folders.
        allowed_portal_types = [
            fti.getId() for fti in self.actual_context.allowedContentTypes()
        ]
        query = {
            "context": self.source_object,
            "depth": 1,
            "portal_type": allowed_portal_types,
        }
        # Get the search parameters from the widget.
        query.update(self.query)
        selectable = api.content.find(**query)
        selectable_uids = {brain.UID for brain in selectable}

        # First get the folderish items in the results.
        # Include a boolean saying if they are selectable or not.
        results = []
        for folder in folders:
            folder_selectable = folder.UID in selectable_uids
            if folder_selectable:
                # Remove the uid, so we can avoid duplication when including
                # the rest of the selectable items later.
                selectable_uids.remove(folder.UID)
            results.append((folder, folder_selectable))

        # If any selectable items are left, include them.
        if selectable_uids:
            for item in selectable:
                if item.UID not in selectable_uids:
                    # This item was already included in the folders.
                    continue
                results.append((item, True))

        return results

    def portal_type_to_icon(self, portal_type):
        """Map the portal_type to an icon.

        In the page template we then use `type-{icon}` as an html class.
        """
        return portal_type.rpartition(".")[-1].replace(" ", "-")

    @cached_property
    def preview(self):
        """Get info on the item that is selected for preview."""
        preview = self.request.form.get(self.name)
        if not preview:
            return
        # Note: this may be None if the UID does not actually exist.
        return api.content.get(UID=preview)

    def type_title(self, portal_type):
        """Map the portal_type to a user friendly title."""
        return get_portal_type_title(portal_type)


@implementer(IFieldWidget)
@adapter(IChoice, CatalogSource, IOSHAContentSkinLayer)
def PIContentBrowserFieldWidget(field, request, extra=None):
    if extra is not None:
        request = extra
    return FieldWidget(field, PIContentBrowserWidget(request))
