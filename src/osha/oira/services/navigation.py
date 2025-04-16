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

    Filter out training questions: we don't want to see them in the side bar.
    They are shown in the training section.
    """

    ignored_portal_types = {
        "euphorie.training_question",
    }
    banned_keys = [
        "brain",  # not serializable
        "parent",  # creates a circular reference
    ]

    def fix_node(self, node):
        """Prepare a node for serialization"""
        # Rename keys to match plone.restapi standards
        mapping = {
            "portal_type": "@type",
            "url": "@id",
            "children": "items",
        }
        for old_key, new_key in mapping.items():
            if old_key in node:
                node[new_key] = node.pop(old_key)

        # Fix the portal_type
        if "@type" in node:
            node["@type"] = node["@type"].replace("-", ".")
            if node["@type"] in self.ignored_portal_types:
                # Completely ignore this node.
                return

        for key in self.banned_keys:
            if key in node:
                del node[key]

        # Fix the solutions (AKA measure title) which is always `Measure`
        if "@type" == "euphorie-solution" and node.get("description"):
            node["title"] = node["description"]

        # Recurse into children
        if "items" in node:
            tree = [self.fix_node(child) for child in node["items"]]
            node["items"] = list(filter(None, tree))

        return node

    def reply(self):
        """We use the navtree tile to get the navigation tree,
        but we have to fiddle with the nodes to have a proper serialization.
        """
        navtree_tile = api.content.get_view("navtree", self.context, self.request)
        navtree_tile.update()
        tree = [self.fix_node(node) for node in navtree_tile.tree]
        tree = list(filter(None, tree))
        return {
            "@id": self.request.getURL(),
            "items": tree,
        }
