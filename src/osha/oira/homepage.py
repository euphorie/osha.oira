# coding=utf-8
"""
NOTE: This class & view are outdated! Please use osha.oira.client.client.View
instead (@@frontpage)
"""
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from euphorie.client.utils import setRequest
from euphorie.content import MessageFactory as _
from five import grok
from json import loads
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from osha.oira.interfaces import IOSHAContentSkinLayer
from osha.oira.interfaces import IProductLayer
from osha.oira.nuplone.widget import LargeTextAreaFieldWidget
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.dexterity.browser import edit
from plone.dexterity.events import EditFinishedEvent
from plone.directives import dexterity
from plone.directives import form
from plone.z3cform import layout
from z3c.form import button
from z3c.form.form import FormTemplateFactory
from zope import schema
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import directlyProvides
from zope.interface import implements
from ZPublisher.BaseRequest import DefaultPublishTraverse

import logging
import os
import requests

log = logging.getLogger(__name__)

grok.templatedir("templates")

DESCRIPTION_CROP_LENGTH = 200


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

    def update(self):
        plt = api.portal.get_tool('portal_languages')
        self.language_info = plt.getAvailableLanguageInformation()
        props = api.portal.get_tool('portal_properties')
        self.json_url = props.site_properties.getProperty(
            'tools_json_url', 'https://oiraproject.eu/oira-ws/tools.json')

        self.tools = self.prepare_tools()

        return self.render()

    def get_json(self):
        tools_json = requests.get(self.json_url)
        return loads(tools_json.content)

    @property
    def cached_json(self):
        from plone.protect.auto import safeWrite
        safeWrite(self.context, self.request)
        now = datetime.now()
        short_cache = now + timedelta(minutes=5)
        long_cache = now + timedelta(minutes=15)
        if self.request.get('invalidate-cache'):
            mtool = api.portal.get_tool('portal_membership')
            if mtool.checkPermission('cmf.ModifyPortalContent', self.context):
                self.context.cache_until = now

        if not hasattr(self.context, 'json'):
            try:
                self.context.json = self.get_json()
                self.context.cache_until = long_cache
            except (ValueError, AttributeError), err:
                log.error(
                    'Failed to retrieve tools JSON from {}: {}'
                    .format(self.json_url, err)
                )
                return []
        if now >= getattr(self.context, 'cache_until', datetime.min):
            try:
                self.context.json = self.get_json()
                self.context.cache_until = long_cache
            except (ValueError, AttributeError), err:
                log.error(
                    'Failed to update tools JSON from {}: {}'
                    .format(self.json_url, err)
                )
                self.context.cache_until = short_cache
        return self.context.json

    def prepare_tools(self):
        langs = dict()
        cnts = dict()
        ploneview = getMultiAdapter(
            (self.context, self.request), name="plone")
        tools = []
        for entry in self.cached_json:
            if not entry['language_code']:
                continue
            if entry['language_code'] in langs:
                langs[entry['language_code']] += 1
            else:
                langs[entry['language_code']] = 1
            if entry['country_name'] in cnts:
                cnts[entry['country_name']] += 1
            else:
                cnts[entry['country_name']] = 1
            if len(entry['body']) > DESCRIPTION_CROP_LENGTH:
                entry['body_intro'] = ploneview.cropText(
                    entry['body'], DESCRIPTION_CROP_LENGTH)
            else:
                entry['body_intro'] = ""
            tools.append(entry)
        lkeys = sorted(langs.keys())
        langinfo = OrderedDict()
        for lang in lkeys:
            langinfo[lang] = langs[lang]
        self.languages = langinfo

        ckeys = sorted(cnts.keys())
        cntinfo = OrderedDict()
        for country in ckeys:
            cntinfo[country] = cnts[country]
        self.countries = cntinfo

        return tools

    def get_language_name(self, code=''):
        code = code or ''
        if code in self.language_info:
            return self.language_info.get(code)['native']
        return u"N. a."


class Edit(form.SchemaEditForm):
    """ Override to allow us to set form title and bu tton labels """
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
