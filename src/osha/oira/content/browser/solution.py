# coding=utf-8
from euphorie.content.browser import solution
from osha.oira import _


class SolutionView(solution.SolutionView):
    pass


class AddForm(solution.AddForm):
    def updateFields(self):
        super(AddForm, self).updateFields()
        self.buttons["save"].title = _(u"button_save_changes", default=u"Save changes")
        self.buttons["cancel"].title = _(u"button_cancel", default=u"Cancel")

    @property
    def label(self):
        return _(u"Add Solution", default=u"Add Measure")


class AddView(solution.AddView):
    form = AddForm


class EditForm(solution.EditForm):
    """ Override to allow us to set form title and button labels """

    def updateFields(self):
        super(EditForm, self).updateFields()
        self.buttons["save"].title = _(u"button_save_changes", default=u"Save changes")
        self.buttons["cancel"].title = _(u"button_cancel", default=u"Cancel")

    @property
    def label(self):
        return _(u"Edit Solution", default=u"Edit Measure")
