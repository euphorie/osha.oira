

def walk(node):
    for ifx, sub_node in node.ZopeFind(node, search_sub=0):
        pt = getattr(sub_node, "portal_type", "")
        if pt == "euphorie.sector":
            yield sub_node
        if pt in ("euphorie.country", "euphorie.sectorcontainer"):
            for sub_sub_node in walk(sub_node):
                yield sub_sub_node


def look(walker):
    bad = []
    for item in walker:
        logo = item.logo
        if logo:
            try:
                logo.getSize()
            except:
                bad.append(item)
    return bad
