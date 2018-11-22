# coding=utf-8
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView


class AddForm(DefaultAddForm):

    def updateFields(self):
        ''' Adds a referer to be used when a cancel button is pressed
        '''
        super(AddForm, self).updateFields()
        self.fields = self.fields.omit('login', 'password', 'locked')


class AddView(DefaultAddView):
    ''' Custom form for adding a euphorie sector
    '''
    form = AddForm
