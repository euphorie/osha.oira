# coding=utf-8
from ldap import modlist
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView

import ldap
import six


class MigrateLDAPUsersView(BrowserView):
    ''' View that migrates and list the users

    ipdb> pp dict(pasldap.settings)
    {'cache.cache': True,
     'cache.timeout': 300,
     'groups.attrmap': odict([('rdn', 'cn'), ('id', 'cn'), ('description', 'description'), ('title', 'o'), ('member', 'member'), ('cn', 'cn')]),
     'groups.baseDN': 'ou=groups,dc=my-domain,dc=com',
     'groups.memberOfSupport': False,
     'groups.objectClasses': ['groupOfNames'],
     'groups.queryFilter': '(objectClass=groupOfNames)',
     'groups.scope': 1,
     'server.ignore_cert': False,
     'server.page_size': 1000,
     'server.password': 'secret',
     'server.uri': 'ldap://127.0.0.1:3389',
     'server.user': 'cn=Manager,dc=my-domain,dc=com',
     'users.account_expiration': False,
     'users.attrmap': odict([('rdn', 'cn'), ('id', 'cn'), ('login', 'cn'), ('uid', 'cn'), ('email', 'cn'), ('location', 'cn'), ('fullname', 'cn'), ('cn', 'cn')]),
     'users.baseDN': 'dc=my-domain,dc=com',
     'users.expires_attr': '',
     'users.expires_unit': 0,
     'users.memberOfSupport': False,
     'users.objectClasses': ['organizationalRole'],
     'users.queryFilter': '(objectClass=organizationalRole)',
     'users.scope': 1}
    '''  # noqa: E501

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
        pasldap = self.context.acl_users.pasldap
        conn = ldap.initialize(pasldap.settings['server.uri'])
        conn.simple_bind(
            pasldap.settings['server.user'],
            pasldap.settings['server.password'],
        )
        dn_template = 'cn=%s,{}'.format(pasldap.settings['users.baseDN'])
        for obj in objs:
            ldif = modlist.addModlist({
                'objectclass': [
                    'top',
                    'organizationalRole',
                    'simpleSecurityObject',
                ],
                'cn': obj.getId(),
                'userPassword': '{BCRYPT}%s' % obj.password,
            })
            dn = dn_template % obj.getId()
            try:
                conn.add_s(dn, ldif)
                self.request.response.write('Added %r\n' % dn)
            except ldap.ALREADY_EXISTS:
                pass
            self.grant_roles(obj)

        # Its nice to the server to disconnect and free resources when done
        conn.unbind_s()
        self.request.response.write('OK')
