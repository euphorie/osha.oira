from osha.oira import _
from osha.oira.ploneintranet.interfaces import IQuaiveForm
from osha.oira.ploneintranet.z3cform.miller_columns import PIContentBrowserFieldWidget
from plone import api
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from plone.supermodel.model import Schema
from z3c.form import form
from zope import schema
from zope.interface import implementer


class PanelInsertFromToolSchema(Schema):

    directives.widget(
        "source",
        PIContentBrowserFieldWidget,
    )
    source = schema.Choice(
        title=_("Source"),
        description=_("Source description"),
        source=CatalogSource(),
        required=True,
    )


@implementer(IQuaiveForm)
class PanelInsertFromToolView(AutoExtensibleForm, form.Form):

    schema = PanelInsertFromToolSchema
    label = _("title_panel_insert_from_tool", default="Insert module from other tool")
    description = _(
        "description_panel_insert_from_tool",
        default="Select a module from another tool and insert a copy into this tool.",
    )
    ignoreContext = True

    @property
    def template(self):
        return self.index

    @property
    def target_url(self):
        """Return the URL of the Quaive."""
        return self.request.getHeader("HTTP_REFERER")

    def _handle_insert(self):
        data, errors = self.extractData()
        if errors:
            api.portal.show_message(
                _("Please correct the errors below."), self.request, type="warn"
            )
            return
        source = data.get("source")
        source_obj = source and api.content.get(UID=source)
        if not source_obj:
            api.portal.show_message(_("Source not found."), self.request, type="error")
            return
        api.content.copy(source=source_obj, target=self.context)

    @form.button.buttonAndHandler(_("Insert"), name="insert")
    def handle_insert(self, action):
        self._handle_insert()
        return self.request.response.redirect(self.target_url)

    @form.button.buttonAndHandler(_("Cancel"), name="cancel")
    def handle_cancel(self, action):
        """Cancel button"""
        pass

    def updateActions(self):
        super().updateActions()
        for action in self.actions.values():
            if action.__name__ == "cancel":
                action.type_override = "button"
                action.addClass("secondary")
            action.addClass("pat-button close-panel")
