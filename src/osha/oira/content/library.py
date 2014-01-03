import collections
from zExceptions import NotFound
from Acquisition import aq_base
from Acquisition import aq_inner
from five import grok
from zope.event import notify
from zope.component import getUtility
from zope.lifecycleevent import ObjectCopiedEvent
from OFS.event import ObjectClonedEvent
from z3c.appconfig.interfaces import IAppConfig
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.dexterity.interfaces import IDexterityContainer
from plonetheme.nuplone.utils import getPortal
from Products.statusmessages.interfaces import IStatusMessage
from euphorie.content.interfaces import IQuestionContainer
from euphorie.content.module import item_depth
from euphorie.content.risk import IRisk
from euphorie.content.survey import ISurvey
from euphorie.content.behaviour.uniqueid import INameFromUniqueId
from euphorie.content.behaviour.uniqueid import get_next_id
from ..interfaces import IOSHAContentSkinLayer
from .. import _


grok.templatedir('templates')


def is_allowed(context, item):
    try:
        context._verifyObjectPaste(item)
    except ValueError:
        return False
    return True


def build_survey_tree(context, root):
    """Build a simple datastructure describing (part of) a survey.

    This implementation does a walk over the content itself. It is possible
    to also do this based on a catalog query, but since we use light-weight
    content items this should be simpler and removes the need to turn a
    catalog result back into a tree.
    """
    tree = {'title': root.title,
            'children': [],
            'url': root.absolute_url(),
            }
    todo = collections.deque([(root, [], tree['children'])])
    normalize = getUtility(IIDNormalizer).normalize
    while todo:
        (node, index, child_list) = todo.popleft()
        for (ix, child) in enumerate(node.values(), 1):
            if not (IQuestionContainer.providedBy(child) or IRisk.providedBy(child)):
                continue
            child_index = index + [str(ix)]
            info = {'title': child.title,
                    'children': [],
                    'number': '.'.join(child_index),
                    'path': '/'.join(child.getPhysicalPath()),
                    'url': child.absolute_url(),
                    'disabled': not is_allowed(context, child),
                    'portal_type': normalize(child.portal_type),
                    }
            child_list.append(info)
            todo.append((child, child_index, info['children']))
    return tree


class Library(grok.View):
    grok.context(IQuestionContainer)
    grok.layer(IOSHAContentSkinLayer)
    grok.require('euphorie.content.AddNewRIEContent')
    grok.template('library')

    def contents(self):
        return build_survey_tree(aq_inner(self.context), self._library)

    def _get_library(self):
        config = getUtility(IAppConfig).get('euphorie', {})
        path = config.get('library', '').lstrip('/')
        if not path:
            return None
        site = getPortal(self.context)
        library = site.restrictedTraverse(path)
        if not ISurvey.providedBy(library):
            return None
        return library

    def update(self):
        self._library = self._get_library()
        if self._library is None:
            raise NotFound(self, 'library', self.request)
        self.depth = item_depth(aq_inner(self.context))
        self.at_root = not self.depth
        super(Library, self).update()


def assign_ids(context, tree):
    todo = collections.deque([tree])
    while todo:
        item = todo.popleft()
        if INameFromUniqueId.providedBy(item):
            item.id = get_next_id(context)
        if IDexterityContainer.providedBy(item):
            todo.extend(item.values())


class LibraryInsert(grok.View):
    grok.name('library-insert')
    grok.context(IQuestionContainer)
    grok.layer(IOSHAContentSkinLayer)
    grok.require('euphorie.content.AddNewRIEContent')

    def render(self):
        if self.request.method != 'POST':
            raise NotFound(self, 'library-insert', self.request)
        path = self.request.form.get('path')
        if not path:
            raise NotFound(self, 'library-insert', self.request)  # XXX Wrong exception type
        target = aq_inner(self.context)
        app = target.getPhysicalRoot()
        source = app.restrictedTraverse(path)
        if not is_allowed(target, source):
            raise NotFound(self, 'library-insert', self.request)  # XXX Wrong exception type
        copy = source._getCopy(target)
        import ipdb ; ipdb.set_trace()
        assign_ids(target, copy)
        notify(ObjectCopiedEvent(copy, source))
        target._setObject(copy.id, copy, suppress_events=True)
        copy = target[copy.id]
        copy._postCopy(target, op=0)
        notify(ObjectClonedEvent(copy))

        IStatusMessage(self.request).addStatusMessage(
                _(u'Addded a copy of "${title}" to your survey.',
                    mapping={'title': copy.title}),
                type='success')
        self.response.redirect(copy.absolute_url())
