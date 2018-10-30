# coding=utf-8
from euphorie.content.country import ManageUsers as EuphorieManageUsers
from five import grok
from osha.oira.interfaces import IOSHAContentSkinLayer
from plone import api

import six


grok.templatedir('templates')


class ManageUsers(EuphorieManageUsers):
    grok.layer(IOSHAContentSkinLayer)
    grok.template('user_mgmt')

    _country_manager_roles = (
        'Contributor',
        'CountryManager',
        'Editor',
        'Reader',
        'Reviewer',
    )

    def get_user(self, userid):
        ''' Takes the user info as returned by the enumerateUsers method
        and resolve the user
        '''
        return api.user.get(userid=userid)

    def is_manager(self, user):
        ''' Check if this user is a manager for this country
        '''
        return 'CountryManager' in api.user.get_roles(
            user=user,
            obj=self.context,
        )

    def ldap_userids(self):
        ''' Return the LDAP users
        '''
        api.portal.show_message('ciao', self.request)
        au = api.portal.get_tool('acl_users')
        ldap = au.pasldap
        return [result['id'] for result in ldap.enumerateUsers()]

    def maybe_manage_ldap_managers(self):
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
            return api.user.grant_roles(
                user=user,
                roles=self._country_manager_roles,
                obj=self.context,
            )
        if ldap_action == 'revoke':
            return api.user.revoke_roles(
                user=user,
                roles=self._country_manager_roles,
                obj=self.context,
            )

    def update(self):
        self.maybe_manage_ldap_managers()
        return super(ManageUsers, self).update()
