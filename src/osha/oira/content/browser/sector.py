from euphorie.content.browser import sector
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView


class AddForm(DefaultAddForm):
    def updateFields(self):
        """Adds a referer to be used when a cancel button is pressed."""
        super().updateFields()
        self.fields = self.fields.omit(
            "login", "password", "locked", "contact_name", "contact_email"
        )


class AddView(DefaultAddView):
    """Custom form for adding a euphorie sector."""

    form = AddForm


class EditForm(sector.EditForm):

    def updateFields(self):
        super().updateFields()
        self.fields = self.fields.omit(
            "title", "login", "locked", "password", "contact_name", "contact_email"
        )
