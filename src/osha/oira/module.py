from five import grok
from zope.component import getUtility

from plone.directives import dexterity
from plone.dexterity.interfaces import IDexterityFTI

from euphorie.content import MessageFactory as _
from euphorie.content.module import IModule
from euphorie.content.module import View as ModuleView
from euphorie.client.module import EvaluationView as ModuleEvaluationView
from euphorie.client.module import ActionPlanView as ModuleActionPlanView
from euphorie.client.module import IdentificationView as \
                                        ModuleIdentificationView

import interfaces

grok.templatedir("templates")

class View(ModuleView):
    grok.template("module_view")

    @property
    def portal_type(self):
        if self.context.aq_parent.portal_type  == 'euphorie.module':
            return _('Submodule')
        else:
            portal_type = self.context.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            return fti.Title()

class EvaluationView(ModuleEvaluationView):
    grok.layer(interfaces.IOSHAEvaluationPhaseSkinLayer)
    grok.template("module_evaluation")

class IdentificationView(ModuleIdentificationView):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("module_identification")

class ActionPlanView(ModuleActionPlanView):
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("module_actionplan")


class Edit(dexterity.EditForm):
    grok.context(IModule)

    @property
    def label(self):
        if self.context.aq_parent.portal_type  == 'euphorie.module':
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
        if self.context.portal_type  == 'euphorie.module':
            type_name = _('Submodule')
        else:
            portal_type = self.portal_type
            fti = getUtility(IDexterityFTI, name=portal_type)
            type_name = fti.Title()
        return _(u"Add ${name}", mapping={'name': type_name})

