# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView

import six


class BaseManageLDAPUsersView(BrowserView):

    _roles = set([])

    @property
    @memoize
    def sorted_roles(self):
        return list(sorted(self._roles))

    @memoize_contextless
    def get_user(self, userid):
        ''' Takes the user info as returned by the enumerateUsers method
        and resolve the user
        '''
        return api.user.get(userid=userid)

    @memoize
    def get_local_roles(self, user):
        return set(api.user.get_roles(
            user=user,
            obj=self.context,
        ))

    def has_managed_roles(self, user):
        ''' Check if user has the roles we are managing here
        '''
        return not (self._roles - self.get_local_roles(user))

    def ldap_userids(self):
        ''' Return the LDAP users
        '''
        api.portal.show_message('ciao', self.request)
        au = api.portal.get_tool('acl_users')
        ldap = au.pasldap
        return [result['id'] for result in ldap.enumerateUsers()]

    def maybe_manage_local_roles(self):
        '''
        '''
        ldap_action = self.request.get('ldap_action')
        if not isinstance(ldap_action, six.string_types):
            return
        userid = self.request.get('userid')
        if not isinstance(userid, six.string_types):
            return
        user = self.get_user(userid)
        if not user:
            return
        if ldap_action == 'grant':
            api.user.grant_roles(
                user=user,
                roles=self.sorted_roles,
                obj=self.context,
            )
        elif ldap_action == 'revoke':
            api.user.revoke_roles(
                user=user,
                roles=self.sorted_roles,
                obj=self.context,
            )

    def __call__(self):
        self.maybe_manage_local_roles()
        return super(BaseManageLDAPUsersView, self).__call__()


class ManageCountryLDAPUsersView(BaseManageLDAPUsersView):

    _roles = {
        'Contributor',
        'CountryManager',
        'Editor',
        'Reader',
        'Reviewer',
    }


class ManageSectorLDAPUsersView(BaseManageLDAPUsersView):
    _roles = {
        'Sector',
    }
