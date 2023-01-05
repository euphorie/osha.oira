from osha.oira.nuplone.interfaces import IOiRAFormLayer
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from zope.interface import Interface


class IProductLayer(Interface):
    """Marker interface for requests indicating the osha.oira package has been
    installed."""


class IOSHAContentSkinLayer(IOiRAFormLayer, NuPloneSkin):
    """Marker interface for the CMS/Content editing skin."""
