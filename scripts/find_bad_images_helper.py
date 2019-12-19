from plone.namedfile.interfaces import INamedFile
from ZODB.POSException import POSKeyError
from Products.CMFCore.interfaces import IFolderish

"""
Usage:
bin/instance debug
# fetch folderish item, e.g. a country:
item = app.Plone2.sectors.cy
recurse(cy)

Note: recurse() can call both check_dexterity_blobs and check_annotation_blobs,
either at the same go, or independently
"""


def check_annotation_blobs(context):
    trouble = False
    ann = getattr(context, "__annotations__", None)
    if not ann:
        return
    scales = context.__annotations__.get('plone.scale', {})
    for key, item in scales.items():
        img = item.get('data')
        if img:
            try:
                img.getSize()
            except:
                scales.pop(key)
                trouble = True
    return trouble


def check_dexterity_blobs(context):
    trouble = False
    for key, value in context.__dict__.items():
        # Ignore non-contentish attributes to speed up us a bit
        if not key.startswith("_"):
            if INamedFile.providedBy(value):
                try:
                    value.getSize()
                except POSKeyError:
                    print "Found damaged Dexterity plone.app.NamedFile %s on %s" % (key, context.absolute_url())
                    trouble = True
                    setattr(context, key, None)
    return trouble


def fix_blobs(context):
    if check_dexterity_blobs(context):
        print "Bad blobs found on %s" % context.absolute_url()


def fix_annotation_blobs(context):
    if check_annotation_blobs(context):
        print "Bad annotation blobs found on %s" % context.absolute_url()


def recurse(tree):
    """ Walk through all the content on a Plone site """
    for id, child in tree.contentItems():
        fix_blobs(child)
        fix_annotation_blobs(child)
        if IFolderish.providedBy(child):
            recurse(child)


# def walk(node):
#     for ifx, sub_node in node.ZopeFind(node, search_sub=0):
#         pt = getattr(sub_node, "portal_type", "")
#         if pt == "euphorie.survey":
#             yield sub_node
#         if pt in ("euphorie.country", "euphorie.sector", "euphorie.sectorcontainer", "euphorie.surveygroup"):
#             for sub_sub_node in walk(sub_node):
#                 yield sub_sub_node


# def look(walker):
#     bad = []
#     for item in walker:
#         logo = getattr(item, "external_site_logo", None)
#         if logo:
#             try:
#                 logo.getSize()
#             except:
#                 bad.append(item)
#     return bad

# walker = walk(portal)
