# coding=utf-8
from ..interfaces import IProductLayer
from .interfaces import IOSHAClientSkinLayer
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from euphorie.client import client
from euphorie.client.api.entry import access_api
from euphorie.client.client import IClient
from five import grok
from json import loads
from plone import api
from plone.protect.auto import safeWrite
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IBrowserSkinType
from ZPublisher.BaseRequest import DefaultPublishTraverse
import logging
import requests

DESCRIPTION_CROP_LENGTH = 200
log = logging.getLogger(__name__)


grok.templatedir("templates")


class ClientPublishTraverser(DefaultPublishTraverse):
    """Publish traverser to setup the skin layer.

    This traverser marks the request with IOSHAClientSkinLayer when the
    client is traversed and the osha.oira product is installed.
    """
    adapts(IClient, IProductLayer)

    def publishTraverse(self, request, name):
        from euphorie.client.utils import setRequest
        setRequest(request)
        request.client = self.context
        if name == 'api':
            return access_api(request).__of__(self.context)

        ifaces = [iface for iface in directlyProvidedBy(request)
                  if not IBrowserSkinType.providedBy(iface)]
        directlyProvides(request, IOSHAClientSkinLayer, ifaces)
        return super(ClientPublishTraverser, self).publishTraverse(request, name)


class View(client.View):
    """View name: @@view
    """
    grok.layer(IOSHAClientSkinLayer)
    grok.template("frontpage")

    def update(self):
        plt = api.portal.get_tool('portal_languages')
        self.language_info = plt.getAvailableLanguageInformation()
        self.tools = self.prepare_tools()
        return self.render()

    def get_json(self):
        tools_json = requests.get(self.json_url)
        return loads(tools_json.content)

    @property
    def json_url(self):
        props = api.portal.get_tool('portal_properties')
        return props.site_properties.getProperty('tools_json_url', None)

    @property
    def cached_json(self):
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
