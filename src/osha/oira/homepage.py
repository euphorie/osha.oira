import os
from five import grok
from zope import schema
from zope.component import adapts
from zope.event import notify
from zope.interface import directlyProvides
from zope.interface import implements

from ZPublisher.BaseRequest import DefaultPublishTraverse

from z3c.form import button
from z3c.form.form import FormTemplateFactory
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.dexterity.browser import edit
from plone.dexterity.events import EditFinishedEvent
from plone.directives import dexterity
from plone.directives import form
from plone.z3cform import layout

from euphorie.content import MessageFactory as _
from euphorie.client.utils import setRequest

from osha.oira.client.interfaces import IOSHAClientSkinLayer
from osha.oira.interfaces import IOSHAContentSkinLayer
from osha.oira.interfaces import IProductLayer
from osha.oira.nuplone.widget import LargeTextAreaFieldWidget


grok.templatedir("templates")


class IHomePage(form.Schema, IBasic):
    """ Custom user editable homepage
    """
    description = schema.Text(
        title=_("label_homepage_description", u"HTML Source Code"))
    form.widget(description=LargeTextAreaFieldWidget)


class HomePage(dexterity.Container):
    implements(IHomePage)


class View(grok.View):
    grok.context(IHomePage)
    grok.require("zope2.View")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("custom_homepage")
    grok.name("nuplone-view")

    def render_body(self):
        return self.context.description


class Edit(form.SchemaEditForm):
    """ Override to allow us to set form title and button labels """
    grok.context(IHomePage)
    grok.require("cmf.ModifyPortalContent")
    grok.layer(IOSHAContentSkinLayer)
    grok.name("edit")

path = lambda p: os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'templates', p)

homepage_form_factory = FormTemplateFactory(
        path('homepage_form.pt'), form=Edit)

class HomePagePublishTraverser(DefaultPublishTraverse):
    """Publish traverser to setup the skin layer.

    This traverser marks the request with IOSHAClientSkinLayer when the
    client is traversed and the osha.oira product is installed.
    """
    adapts(IHomePage, IProductLayer)

    def publishTraverse(self, request, name):
        setRequest(request)
        request.client = self.context
        directlyProvides(request, IOSHAClientSkinLayer)
        return super(HomePagePublishTraverser,
                     self).publishTraverse(request, name)


class EditForm(edit.DefaultEditForm):
    """ """
    buttons = edit.DefaultEditForm.buttons
    preview = button.Buttons(button.Button('preview',
                                           title=u'Save and preview'))
    buttons = preview + buttons
    buttons['cancel'].title = _(u'Clear unsaved changes')
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
