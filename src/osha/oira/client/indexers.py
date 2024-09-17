from AccessControl.PermissionRole import rolesForPermissionOn
from plone.indexer import indexer
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface


@indexer(Interface)
def managerRolesAndUsers(obj):
    """Index the roles and users that have the `Euphorie: Manage country`
    permission on the object.

    Used in regulating access to mailing lists.
    Modeled after `allowedRolesAndUsers` from standard Plone."""
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
