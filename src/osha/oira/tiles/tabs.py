# coding=utf-8
from euphorie.content import MessageFactory as _
from euphorie.content.sector import ISector
from euphorie.deployment.tiles.tabs import SiteRootTabsTile
from plone.memoize.ram import cache
from plone.memoize.view import memoize

import re


class OiRASiteRootTabsTile(SiteRootTabsTile):

    _custom_current_map = [
        (re.compile(r"/sectors/[a-z]+/(.*)@@manage-ldap-users"), "ldapmgmt"),
    ]

    @property
    @cache(lambda *args: 1)
    def current_map(self):
        current_map = []
        current_map.extend(self._custom_current_map)
        current_map.extend(super(OiRASiteRootTabsTile, self).current_map)
        return current_map

    @memoize
    def get_current_sector(self):
        for obj in self.context.aq_chain:
            if ISector.providedBy(obj):
                return obj

    def update(self):
        super(OiRASiteRootTabsTile, self).update()
        is_country = self.get_current_country() == self.context
        is_sector = self.get_current_sector() == self.context
        for r in self.tabs:
            if r.get("id") == "help":
                self.tabs.remove(r)
            elif r.get("id") == "usermgmt":
                r["title"] = _("nav_sectormanagement", default=u"Sector management")
        if self.is_country_manager() and (is_sector or is_country):
            if is_sector:
                title = _("nav_ldapmanagement_sector", default=u"Manage sector access")
            else:
                title = _(
                    "nav_ldapmanagement_country", default=u"Manage country access"
                )
            custom_tab = {
                "id": "ldapmgmt",
                "title": title,
                "url": "%s/@@manage-ldap-users" % self.context.absolute_url(),
                "class": "current"
                if self.get_current_url() == "ldapmgmt"
                else None,  # noqa: E501
            }
            self.tabs.insert(2, custom_tab)
