from five import grok
from euphorie.content.solution import ISolution
from euphorie.content.solution import View as BaseView
from plone.directives import form
from plone.directives import dexterity
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from ..interfaces import IOSHAContentSkinLayer
from .. import _

grok.templatedir("templates")


class View(BaseView):
    """ Override so that we can use out own template (only needed for one
        translation).
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        XXX: If the view is bound to IOSHAContentSkinLayer instead of NuPloneSkin,
        then it will NOT be used.
        Only by giving it the SAME layer as the view it is supposed to override
        can we make sure this view is actually used. I have no idea why this
        works for all other content types but not for solution.
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """
    grok.context(ISolution)
    grok.require("zope2.View")
    grok.layer(NuPloneSkin)
    grok.name("nuplone-view")
    grok.template("solution_view")


class SolutionEdit(form.SchemaEditForm):
    """ Override to allow us to set form title and button labels """
    grok.context(ISolution)
    grok.require("cmf.ModifyPortalContent")
    grok.layer(IOSHAContentSkinLayer)
    grok.name("edit")

    def updateFields(self):
        super(SolutionEdit, self).updateFields()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")

    @property
    def label(self):
        return _(u"Edit Solution", default=u"Edit Measure")


class SolutionAdd(dexterity.AddForm):
    """ Override to allow us to set form title and button labels """
    grok.context(ISolution)
    grok.name("euphorie.solution")
    grok.require("euphorie.content.AddNewRIEContent")

    def updateFields(self):
        super(SolutionAdd, self).updateFields()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")

    @property
    def label(self):
        return _(u"Add Solution", default=u"Add Measure")
