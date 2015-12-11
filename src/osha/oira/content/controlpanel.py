from plone.app.controlpanel.site import SiteControlPanel as SiteControlPanelBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SiteControlPanel(SiteControlPanelBase):
    """A simple form to be used as a basis for control panel screens."""

    template = ViewPageTemplateFile('templates/control-panel.pt')
