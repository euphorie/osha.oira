# coding=utf-8
from ..interfaces import IProductLayer
from .interfaces import IOSHAClientSkinLayer
from Acquisition import aq_base
from euphorie.client import client
from euphorie.client.api.entry import access_api
from euphorie.client.client import IClient
from euphorie.client.country import IClientCountry
from five import grok
from plone.memoize.instance import memoize
from z3c.appconfig.interfaces import IAppConfig
from zope.component import adapts
from zope.component import getUtility
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IBrowserSkinType
from ZPublisher.BaseRequest import DefaultPublishTraverse
import logging
try:
    from plone.protect.auto import safeWrite
except ImportError:
    # This can happen in our functional tests. We need to pin plone.protect
    # to 2.0.2, otherwise registerUserInClient() from euphorie.client.tests.utils
    # fails.
    def safeWrite(context, request):
        pass


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

    @property
    @memoize
    def default_country(self):
        appconfig = getUtility(IAppConfig)
        settings = appconfig.get('euphorie')
        return settings.get('default_country', 'eu')

    def update(self):

        """ The frontpage has been disbanded. We redirect to the country that
        is defined as the default, or pick a random country.
        """
        target = None
        language = self.request.form.get("language")
        url_param = language and "?language=%s" % language or ""
        if self.default_country:
            if getattr(aq_base(self.context), self.default_country, None):
                found = getattr(self.context, self.default_country)
                if IClientCountry.providedBy(found):
                    target = found
        while not target:
            for id, found in self.context.objectItems():
                if IClientCountry.providedBy(found):
                    target = found
        self.request.RESPONSE.redirect("{}{}".format(
            target.absolute_url(), url_param))
