# fmt: off
from Products.CMFPlone.controlpanel.browser.site import SiteControlPanel as SiteControlPanelBase  # noqa: E501
# fmt: on
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SiteControlPanel(SiteControlPanelBase):
    """A simple form to be used as a basis for control panel screens."""

    template = ViewPageTemplateFile("templates/control-panel.pt")
