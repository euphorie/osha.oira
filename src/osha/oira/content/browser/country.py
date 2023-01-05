from euphorie.content.browser.country import ManageUsers
from euphorie.content.countrymanager import ICountryManager
from euphorie.content.sector import ISector


class OSHAManageUsers(ManageUsers):
    @property
    def sectors(self):
        sectors_list = []
        for sector in self.country.values():
            if not ISector.providedBy(sector):
                continue
            entry = {
                "id": sector.id,
                "login": sector.login,
                "password": sector.password,
                "title": sector.title,
                "url": sector.absolute_url(),
                "locked": sector.locked,
                "contact_email": sector.contact_email,
            }
            view = sector.restrictedTraverse("manage-ldap-users", None)
            if not view:
                entry["managers"] = []
            else:
                entry["managers"] = [
                    userid
                    for userid in view.local_roles_userids()
                    if view.get_user(userid)
                ]
            sectors_list.append(entry)

        sectors_list.sort(key=lambda s: s["title"].lower())
        return sectors_list

    @property
    def managers(self):
        managers_list = [
            {
                "id": manager.id,
                "login": manager.login,
                "title": manager.title,
                "url": manager.absolute_url(),
                "locked": manager.locked,
                "contact_email": manager.contact_email,
            }
            for manager in self.country.values()
            if ICountryManager.providedBy(manager)
        ]
        managers_list.sort(key=lambda s: s["title"].lower())
        return managers_list
