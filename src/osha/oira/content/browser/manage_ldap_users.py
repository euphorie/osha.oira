# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView

import six


class BaseManageLDAPUsersView(BrowserView):

    _roles = set([])

    @property
    @memoize_contextless
    def ldap(self):
        au = api.portal.get_tool('acl_users')
        return au.pasldap

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

    def local_roles_userids(self):
        lr = self.context.__ac_local_roles__
        return sorted(
            userid for userid in lr if 'Owner' not in lr[userid]
        )

    def has_managed_roles(self, user):
        ''' Check if user has the roles we are managing here
        '''
        return not (self._roles - self.get_local_roles(user))

    def ldap_userids(self):
        ''' Return the LDAP users
        '''
        query = self.request.form.get('SearchableText', '')
        return self.enumerateUsersIds(query)

    def enumerateUsersIds(self, query=''):
        if not query:
            return []
        query = '*%s*' % query
        results = self.ldap.enumerateUsers(query) or ()
        return sorted(result['id'] for result in results)

    def grant_roles(self, user):
        api.user.grant_roles(
            user=user,
            roles=self.sorted_roles,
            obj=self.context,
        )

    def revoke_roles(self, user):
        api.user.revoke_roles(
            user=user,
            roles=self.sorted_roles,
            obj=self.context,
        )

    def maybe_manage_local_roles(self):
        ''' Check the request and see if we should mange some user local roles
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
            self.grant_roles(user)
        elif ldap_action == 'revoke':
            self.revoke_roles(user)

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
