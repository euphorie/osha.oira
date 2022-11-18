from euphorie.client.browser.settings import Preferences
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class OSHAPreferences(Preferences):
    """ """

    template = ViewPageTemplateFile("templates/preferences.pt")
