from euphorie.content.browser import sector
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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
    template = ViewPageTemplateFile("templates/sector_edit.pt")

    def extractData(self):
        unwanted_fields = ("locked", "password", "contact_name", "contact_email")
        self.fields = self.fields.omit(*unwanted_fields)
        for key in unwanted_fields:
            if key in self.widgets:
                del self.widgets[key]
        return super().extractData()
