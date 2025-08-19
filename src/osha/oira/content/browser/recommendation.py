from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm


class AddForm(DefaultAddForm):
    """Override to allow us to dynamically set field descriptions."""


class AddView(DefaultAddView):
    form = AddForm


class EditForm(DefaultEditForm):
    """Override to allow us to dynamically set field descriptions."""
