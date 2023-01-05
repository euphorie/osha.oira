from ..interfaces import IProductLayer
from .interfaces import IOSHAClientSkinLayer
from euphorie.client.client import IClient
from zope.component import adapter
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


@adapter(IClient, IProductLayer)
class ClientPublishTraverser(DefaultPublishTraverse):
    """Publish traverser to setup the skin layer.

    This traverser marks the request with IOSHAClientSkinLayer when the
    client is traversed and the osha.oira product is installed.
    """

    def publishTraverse(self, request, name):
        from euphorie.client.utils import setRequest

        setRequest(request)
        request.client = self.context

        ifaces = [
            iface
            for iface in directlyProvidedBy(request)
            if not IBrowserSkinType.providedBy(iface)
        ]
        directlyProvides(request, IOSHAClientSkinLayer, ifaces)
        return super().publishTraverse(request, name)
