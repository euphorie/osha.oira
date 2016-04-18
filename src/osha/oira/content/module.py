from five import grok
from zope.component import getUtility
from plone.directives import dexterity
from plone.dexterity.interfaces import IDexterityFTI
from euphorie.content import MessageFactory as _
from euphorie.content import module
from euphorie.content.module import IModule
from euphorie.content.module import View as ModuleView
from zope import interface
from .risk import IRiskAdditionalContent, RiskAdditionalContent
from ..interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class IOSHAModuleMarker(IModule):
    """ Marker interface so that we can register more specific adapters for
        OSHA's survey object.
    """

interface.classImplements(module.Module, IOSHAModuleMarker)


class IModuleAdditionalContent(IRiskAdditionalContent):
    """
        We need to define our own interface, so that Risks won't inherit
        files set on their parent module
    """
    pass


class ModuleAdditionalContent(RiskAdditionalContent):
    pass


class IOSHAModule(IModule, IModuleAdditionalContent):
    pass


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


class Edit(module.Edit):
    grok.context(IModule)
    grok.layer(IOSHAContentSkinLayer)

    def __init__(self, context, request):
        module.Edit.__init__(self, context, request)
        self.schema = IOSHAModule

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
