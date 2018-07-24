# coding=utf-8
from ..interfaces import IProductLayer
from .interfaces import IOSHAClientSkinLayer
from datetime import datetime
from datetime import timedelta
from euphorie.client.api.entry import access_api
from euphorie.client.client import IClient
from five import grok
from json import loads
from plone import api
try:
    from plone.protect.auto import safeWrite
except ImportError:
    # This can happen in our functional tests. We need to pin plone.protect
    # to 2.0.2, otherwise registerUserInClient() from euphorie.client.tests.utils
    # fails.
    def safeWrite(context, request):
        pass
from zope.component import adapts
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IBrowserSkinType
from ZPublisher.BaseRequest import DefaultPublishTraverse
import logging
import requests

DESCRIPTION_CROP_LENGTH = 200
log = logging.getLogger(__name__)


grok.templatedir("templates")


def cached_tools_json(context, request):
    safeWrite(context, request)
    now = datetime.now()
    short_cache = now + timedelta(minutes=5)
    long_cache = now + timedelta(minutes=15)
    if request.get('invalidate-cache'):
        mtool = api.portal.get_tool('portal_membership')
        if mtool.checkPermission('cmf.ModifyPortalContent', context):
            context.cache_until = now

    if not hasattr(context, 'json'):
        try:
            context.json = get_json()
            context.cache_until = long_cache
        except (ValueError, AttributeError), err:
            log.error(
                'Failed to retrieve tools JSON from {}: {}'
                .format(get_json_url(), err)
            )
            return []
    if now >= getattr(context, 'cache_until', datetime.min):
        try:
            context.json = get_json()
            context.cache_until = long_cache
        except (ValueError, AttributeError), err:
            log.error(
                'Failed to update tools JSON from {}: {}'
                .format(get_json_url(), err)
            )
            context.cache_until = short_cache
    return context.json


def get_json():
    tools_json = requests.get(get_json_url())
    return loads(tools_json.content)


def get_json_url():
    props = api.portal.get_tool('portal_properties')
    return props.site_properties.getProperty('tools_json_url', None)


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
