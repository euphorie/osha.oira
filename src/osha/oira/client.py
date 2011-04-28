from five import grok
from zope.component import adapts
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IBrowserSkinType
from ZPublisher.BaseRequest import DefaultPublishTraverse
from osha.oira.interfaces import IProductLayer
from osha.oira.interfaces import IOSHAClientSkinLayer
from euphorie.client.client import IClient

grok.templatedir("templates")

class View(grok.View):
    grok.context(IClient)
    grok.layer(IOSHAClientSkinLayer)
    grok.template("frontpage")

class ClientPublishTraverser(DefaultPublishTraverse):
    """Publish traverser to setup the skin layer.

    This traverser marks the request with IOSHAClientSkinLayer when the
    client is traversed and the osha.oira product is installed.
    """
    adapts(IClient, IProductLayer)

    def publishTraverse(self, request, name):
        from euphorie.client.utils import setRequest
        setRequest(request)
        request.client=self.context
        ifaces=[iface for iface in directlyProvidedBy(request)
                if not IBrowserSkinType.providedBy(iface)]
        directlyProvides(request, IOSHAClientSkinLayer, ifaces)
        return super(ClientPublishTraverser, self).publishTraverse(request, name)

