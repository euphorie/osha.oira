from euphorie.content.browser import solution
from osha.oira import _


class SolutionView(solution.SolutionView):
    pass


class AddForm(solution.AddForm):
    def updateFields(self):
        super().updateFields()
        self.buttons["save"].title = _("button_save_changes", default="Save changes")
        self.buttons["cancel"].title = _("button_cancel", default="Cancel")

    @property
    def label(self):
        return _("Add Solution", default="Add Measure")


class AddView(solution.AddView):
    form = AddForm


class EditForm(solution.EditForm):
    """Override to allow us to set form title and button labels."""

    def updateFields(self):
        super().updateFields()
        self.buttons["save"].title = _("button_save_changes", default="Save changes")
        self.buttons["cancel"].title = _("button_cancel", default="Cancel")

    @property
    def label(self):
        return _("Edit Solution", default="Edit Measure")
