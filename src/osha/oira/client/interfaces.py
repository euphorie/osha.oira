from euphorie.client.interfaces import IActionPlanPhaseSkinLayer
from euphorie.client.interfaces import IClientSkinLayer
from euphorie.client.interfaces import ICustomizationPhaseSkinLayer
from euphorie.client.interfaces import IEvaluationPhaseSkinLayer
from euphorie.client.interfaces import IIdentificationPhaseSkinLayer
from euphorie.client.interfaces import IItalyActionPlanPhaseSkinLayer
from euphorie.client.interfaces import IItalyCustomizationPhaseSkinLayer
from euphorie.client.interfaces import IItalyEvaluationPhaseSkinLayer
from euphorie.client.interfaces import IItalyIdentificationPhaseSkinLayer
from euphorie.client.interfaces import IItalyReportPhaseSkinLayer
from euphorie.client.interfaces import IReportPhaseSkinLayer


class IOSHAClientSkinLayer(IClientSkinLayer):
    """Marker interface for the OSHA client skin."""


class IOSHAIdentificationPhaseSkinLayer(IIdentificationPhaseSkinLayer):
    """Skin layer used during the identification phase."""


class IOSHAEvaluationPhaseSkinLayer(IEvaluationPhaseSkinLayer):
    """Skin layer used during the evaluation phase."""


class IOSHAActionPlanPhaseSkinLayer(IActionPlanPhaseSkinLayer):
    """Skin layer used during the action plan phase."""


class IOSHACustomizationPhaseSkinLayer(ICustomizationPhaseSkinLayer):
    """Skin layer used during the action plan report phase."""


class IOSHAReportPhaseSkinLayer(IReportPhaseSkinLayer):
    """Skin layer used during the action plan report phase."""


class IOSHAItalyIdentificationPhaseSkinLayer(IItalyIdentificationPhaseSkinLayer, IOSHAIdentificationPhaseSkinLayer):  # noqa
    """Special for Italy"""


class IOSHAItalyEvaluationPhaseSkinLayer(IItalyEvaluationPhaseSkinLayer, IOSHAEvaluationPhaseSkinLayer):  # noqa
    """Special for Italy"""


class IOSHAItalyActionPlanPhaseSkinLayer(IItalyActionPlanPhaseSkinLayer, IOSHAActionPlanPhaseSkinLayer):  # noqa
    """Special for Italy"""


class IOSHAItalyCustomizationPhaseSkinLayer(IItalyCustomizationPhaseSkinLayer, IOSHACustomizationPhaseSkinLayer):  # noqa
    """Special for Italy"""


class IOSHAItalyReportPhaseSkinLayer(IItalyReportPhaseSkinLayer, IOSHAReportPhaseSkinLayer):  # noqa
    """Special for Italy"""
