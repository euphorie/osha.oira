from zope.interface import Interface
from euphorie.client import interfaces
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from osha.oira.z3cform.interfaces import IOiRAFormLayer

class IProductLayer(Interface):
    """Marker interface for requests indicating the osha.oira
       package has been installed.
    """

class IOSHAContentFormLayer(IOiRAFormLayer, NuPloneSkin):
    """Marker interface for the CMS/Content editing skin."""

class IOSHAContentSkinLayer(NuPloneSkin):
    """Marker interface for the CMS/Content editing skin."""

class IOSHAClientSkinLayer(interfaces.IClientSkinLayer):
    """Marker interface for the OSHA client skin."""

class IOSHAIdentificationPhaseSkinLayer(interfaces.IIdentificationPhaseSkinLayer):
    """Skin layer used during the identification phase."""

class IOSHAReportPhaseSkinLayer(interfaces.IReportPhaseSkinLayer):
    """Skin layer used during the action plan report phase."""

class IOSHAEvaluationPhaseSkinLayer(interfaces.IEvaluationPhaseSkinLayer):
    """Skin layer used during the evaluation phase."""

class IOSHAActionPlanPhaseSkinLayer(interfaces.IActionPlanPhaseSkinLayer):
    """Skin layer used during the action plan phase."""
