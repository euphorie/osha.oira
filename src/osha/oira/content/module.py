from five import grok
from zope.component import getUtility
from plone.directives import dexterity
from plone.dexterity.interfaces import IDexterityFTI
from euphorie.content import MessageFactory as _
from euphorie.content.module import IModule
from euphorie.content.module import View as ModuleView
from ..interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class View(ModuleView):
    grok.template("module_view")
    grok.layer(IOSHAContentSkinLayer)

    @property
    def portal_type(self):
        if self.context.aq_parent.portal_type == 'euphorie.module':
            return _('Submodule')
        else:
            portal_type = self.context.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            return fti.Title()


class Edit(dexterity.EditForm):
    grok.context(IModule)

    @property
    def label(self):
        if self.context.aq_parent.portal_type == 'euphorie.module':
            type_name = _('Submodule')
        else:
            portal_type = self.context.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            type_name = fti.Title()
        return _(u"Edit ${name}", mapping={'name': type_name})


class Add(dexterity.AddForm):
    grok.name('euphorie.module')
    grok.context(IModule)

    @property
    def label(self):
        if self.context.portal_type == 'euphorie.module':
            type_name = _('Submodule')
        else:
            portal_type = self.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            type_name = fti.Title()
        return _(u"Add %s" % type_name)
