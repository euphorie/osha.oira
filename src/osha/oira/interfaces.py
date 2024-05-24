from euphorie.content.interfaces import IEuphorieContentLayer
from osha.oira.nuplone.interfaces import IOiRAFormLayer
from zope.interface import Interface


class IProductLayer(Interface):
    """Marker interface for requests indicating the osha.oira package has been
    installed."""


class IOSHAContentSkinLayer(IOiRAFormLayer, IEuphorieContentLayer):
    """Marker interface for the CMS/Content editing skin."""
