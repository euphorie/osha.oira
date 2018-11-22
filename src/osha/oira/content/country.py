# coding=utf-8
from Acquisition import aq_inner
from euphorie.content.country import ManageUsers
from euphorie.content.sector import ISector
from five import grok
from osha.oira.interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class OSHAManageUsers(ManageUsers):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("user_mgmt")

    def update(self):
        from euphorie.content.countrymanager import ICountryManager
        super(OSHAManageUsers, self).update()
        country = aq_inner(self.context)
        self.sectors = [{'id': sector.id,
                         'login': sector.login,
                         'password': sector.password,
                         'title': sector.title,
                         'url': sector.absolute_url(),
                         'locked': sector.locked,
                         'contact_email': sector.contact_email}
                        for sector in country.values()
                        if ISector.providedBy(sector)]
        self.sectors.sort(key=lambda s: s["title"].lower())
        self.managers = [{'id': manager.id,
                          'login': manager.login,
                          'title': manager.title,
                          'url': manager.absolute_url(),
                          'locked': manager.locked,
                          'contact_email': manager.contact_email}
                         for manager in country.values()
                         if ICountryManager.providedBy(manager)]
        self.managers.sort(key=lambda s: s["title"].lower())
