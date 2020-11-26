from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView

import z3c.form


class AddForm(DefaultAddForm):

    portal_type = "euphorie.countrymanager"

    def update(self):
        super(AddForm, self).update()
        self.widgets["password"].mode = z3c.form.interfaces.HIDDEN_MODE


class AddView(DefaultAddView):
    form = AddForm
