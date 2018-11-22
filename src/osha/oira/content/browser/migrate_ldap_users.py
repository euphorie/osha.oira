# coding=utf-8
from logging import getLogger
from plone import api
from Products.Five import BrowserView

log = getLogger(__name__)


class MigrateLDAPUsersView(BrowserView):
    ''' View that allows LDAP users to have roles in countries and sectors
    '''

    def grant_roles(self, obj):
        ''' Grant the proper local roles to this object
        '''
        try:
            view = api.content.get_view(
                'manage-ldap-users',
                obj,
                self.request.clone()
            )
            url = obj.absolute_url()
        except api.exc.InvalidParameterError:
            # This is a country manager
            view = api.content.get_view(
                'manage-ldap-users',
                obj.aq_parent,
                self.request.clone()
            )
            url = obj.aq_parent.absolute_url()
        users = view.enumerateUsersIds(obj.contact_email)
        if users:
            user = api.user.get(users[0])
            if user:
                view.grant_roles(user)
                log.info("Granted roles to %s on %s" % (users[0], url))

    def __call__(self):
        brains = api.content.find(
            portal_type=[
                'euphorie.countrymanager',
                'euphorie.sector',
            ],
        )
        objs = [b.getObject() for b in brains]
        for obj in objs:
            self.grant_roles(obj)
        self.request.response.write('OK')
