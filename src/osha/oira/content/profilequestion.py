from five import grok
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from plone.directives import dexterity
from plone.directives import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from euphorie.content.profilequestion import IProfileQuestion
from euphorie.content.profilequestion import View as BaseView
from ..interfaces import IOSHAContentSkinLayer
from .. import _

grok.templatedir("templates")


class IOSHAProfileQuestion(IProfileQuestion):
    question = schema.TextLine(
        title=_('label_profilequestion_question', default=u'Question'),
        description=_(u'This question must ask users if this profile '
                      u'applies to them.'),
        required=True)

    label_multiple_present = schema.TextLine(
        title=_(u'Multiple item question'),
        required=True)
    form.widget(
        label_multiple_present='euphorie.content.profilequestion.TextSpan7')

    label_single_occurance = schema.TextLine(
        title=_(u'Single occurance prompt'),
        description=_(u'This must ask to user for the name of the '
                      u'relevant location.'),
        required=True)
    form.widget(
        label_single_occurance='euphorie.content.profilequestion.TextSpan7')

    label_multiple_occurances = schema.TextLine(
        title=_(u'Multiple occurance prompt'),
        description=_(u'This must ask to user for the names of all '
                      u'relevant locations.'),
        required=True)
    form.widget(
        label_multiple_occurances='euphorie.content.profilequestion.TextSpan7')


@adapter(IProfileQuestion)
@implementer(IOSHAProfileQuestion)
def context_proxy(content):
    """Trivial adapter to present all standard profile questions implement
    IOSHAProfileQuestion. This allows us to use IOSHAProfileQuestion without
    persisting it or a custom content class in the database so we keep a clean
    migration path.
    """
    return content


class View(BaseView):
    """ Override so that we can use our own template
    """
    grok.template("profilequestion_view")
    grok.layer(IOSHAContentSkinLayer)


class AddForm(dexterity.AddForm):
    grok.context(IProfileQuestion)
    grok.name('euphorie.profilequestion')
    grok.require('euphorie.content.AddNewRIEContent')
    grok.layer(IOSHAContentSkinLayer)
    form.wrap(True)

    schema = IOSHAProfileQuestion
    template = ViewPageTemplateFile('templates/profilequestion_add.pt')

    @property
    def label(self):
        return _(u"Add Profile question")


class EditForm(dexterity.EditForm):
    grok.context(IProfileQuestion)
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IOSHAContentSkinLayer)
    form.wrap(True)

    schema = IOSHAProfileQuestion
    template = ViewPageTemplateFile('templates/profilequestion_add.pt')

    @property
    def label(self):
        return _(u"Edit Profile question")
