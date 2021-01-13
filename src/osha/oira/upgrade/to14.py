# coding=utf-8
from plone import api
from Products.PlonePAS.interfaces.plugins import IUserManagement
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin


def configure_plugins(context):
    au = api.portal.get_tool("acl_users")
    au.pasldap.manage_activateInterfaces(
        [
            "IAuthenticationPlugin",
            "IPropertiesPlugin",
            "IUserEnumerationPlugin",
            "IUserManagement",
        ]
    )
    au.membrane_users.manage_activateInterfaces(
        [
            "IUserAdderPlugin",
            "IUserEnumerationPlugin",
            "IUserIntrospection",
            "IUserManagement",
        ]
    )
    # Move the pasldap plugin up
    for iface in (
        IPropertiesPlugin,
        IUserManagement,
    ):
        while not au.plugins.listPlugins(iface)[0][0] == "pasldap":
            au.plugins.movePluginsUp(iface, ["pasldap"])
