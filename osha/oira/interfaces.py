from euphorie.client import interfaces

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
