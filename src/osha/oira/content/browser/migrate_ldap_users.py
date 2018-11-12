# coding=utf-8
from plone import api
from Products.Five import BrowserView


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
        except api.exc.InvalidParameterError:
            # This is a country manager
            view = api.content.get_view(
                'manage-ldap-users',
                obj.aq_parent,
                self.request.clone()
            )
        view.grant_roles(obj)

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
