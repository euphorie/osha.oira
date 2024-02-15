from AccessControl.PermissionRole import rolesForPermissionOn
from euphorie.client.client import IClient
from plone import api
from plone.indexer import indexer
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface


def is_in_client(obj):
    for parent in obj.aq_chain:
        if IClient.providedBy(parent):
            return True
    return False


@indexer(Interface)
def managerRolesAndUsers(client_obj):
    """For client objects, index the roles and users that have the
    `Euphorie: Manage country` permission on the object's counterpart in the admin
    section, i.e. not the permissions on the object itself are relevant, but its base
    that was copied via the "publish to client" feature.

    Used in regulating access to mailing lists.
    Modeled after `allowedRolesAndUsers` from standard Plone."""
    if not is_in_client(client_obj):
        return None

    sectors = api.portal.get().sectors
    obj = sectors.restrictedTraverse(client_obj.getPhysicalPath()[3:], None)
    if not obj:
        return None

    allowed = set(rolesForPermissionOn("Euphorie: Manage country", obj))
    allowed = allowed | {"Manager", "Sector", "CountryManager"}
    localroles = {}
    try:
        acl_users = getToolByName(obj, "acl_users", None)
        if acl_users is not None:
            localroles = acl_users._getAllLocalRoles(obj)
    except AttributeError:
        localroles = _mergedLocalRoles(obj)
    for user, roles in localroles.items():
        if allowed.intersection(roles):
            allowed.update(["user:" + user])
    if "Owner" in allowed:
        allowed.remove("Owner")
    return list(allowed)
