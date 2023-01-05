from euphorie.client.browser import module
from logging import getLogger
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


logger = getLogger(__name__)


class OSHAIdentificationView(module.IdentificationView):
    """Override the template."""

    template = ViewPageTemplateFile("templates/module_identification.pt")


class OSHAActionPlanView(module.ActionPlanView):
    """Override the template."""
