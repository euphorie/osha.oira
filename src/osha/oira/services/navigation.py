from plone import api
from plone.restapi.services import Service


class NavigationService(Service):
    """This JSON service reuses the navigation tile to serve through the
    REST API the navigation tree of this context.

    The nodes of the tree should be prepared to have a successful
    JSON serialization.

    This method removes the keys:

    - brain (which is not serializable)
    - parent (which will create a circular reference)

    and renames some keys to match the plone.restapi standards:

    - portal_type -> @type
    - url -> @id

    It also fixes the portal_type which is returned normalized
    with a dash instead of a dot.
    """

    def fix_node(self, node):
        """Prepare a node for serialization"""
        banned_keys = [
            "brain",  # now serializable
            "parent",  # creates a circular reference
        ]
        for key in banned_keys:
            if key in node:
                del node[key]

        # Rename keys to math plone.restapi standards
        mapping = {
            "portal_type": "@type",
            "url": "@id",
        }
        for old_key, new_key in mapping.items():
            if old_key in node:
                node[new_key] = node.pop(old_key)

        # Fix the portal_type
        if "@type" in node:
            node["@type"] = node["@type"].replace("-", ".")

        # Recurse into children
        if "children" in node:
            for child in node["children"]:
                self.fix_node(child)

        return node

    def reply(self):
        """We use the navtree tile to get the navigation tree,
        but we have to fiddle with the nodes to have a proper serialization.
        """
        navtree_tile = api.content.get_view("navtree", self.context, self.request)
        navtree_tile.update()
        tree = [self.fix_node(node) for node in navtree_tile.tree]
        return {
            "@id": self.request.getURL(),
            "items": tree,
        }
