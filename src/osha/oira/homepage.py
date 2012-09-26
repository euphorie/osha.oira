from five import grok
from zope import schema
from zope.interface import implements
from zope.event import notify

from z3c.form import button
from plone.z3cform import layout

from plone.directives import form
from plone.directives import dexterity
from plone.dexterity.browser import edit
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.dexterity.events import EditFinishedEvent

from euphorie.content import MessageFactory as _

from osha.oira.interfaces import IOSHAContentSkinLayer
from osha.oira.z3cform.widget import LargeTextAreaFieldWidget

grok.templatedir("templates")

class IHomePage(form.Schema, IBasic):
    """ Custom user editable homepage
    """
    description = schema.Text(
        title = _("label_homepage_description", u"HTML Source Code"))
    form.widget(description=LargeTextAreaFieldWidget)


class HomePage(dexterity.Container):
    implements(IHomePage)


class View(grok.View):
    grok.context(IHomePage)
    grok.require("zope2.View")
    grok.layer(IOSHAContentSkinLayer)
    grok.template("custom_homepage")
    grok.name("nuplone-view")

    def render_body(self):
        return self.context.description


class EditForm(edit.DefaultEditForm):
    """ """
    buttons = edit.DefaultEditForm.buttons
    preview = button.Buttons(button.Button('preview', title=u'Save and preview'))
    buttons = preview + buttons
    buttons['cancel'].title = u'Clear unsaved changes'
    handlers = edit.DefaultEditForm.handlers

    def nextURL(self):
        return 'edit'

    @button.handler(buttons['preview'])
    def handle_preview(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        self.request.response.redirect('nuplone-view')
        notify(EditFinishedEvent(self.context))
    

EditView = layout.wrap_form(EditForm)
