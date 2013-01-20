from five import grok
from euphorie.client import profile
from . import interfaces
from . import _

grok.templatedir("templates")


class OSHAProfile(profile.Profile):
    """ Override the original profile to provide our own template.
    """
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.template("profile")
    grok.name("profile")

    def ProfileQuestions(self):
        return [{'id': child.id,
                 'title': child.title,
                 'question': child.question or child.title,
                 'label_multiple_present': getattr(child,
                     'label_multiple_present',
                     _(u'Does this happen in multiple places?')),
                 'label_single_occurance': getattr(child,
                     'label_single_occurance',
                     _(u'Enter the name of the location')),
                 'label_multiple_occurances': getattr(child,
                     'label_multiple_occurances',
                     _(u'Enter the names of each location')),
                 }
                for child in self.context.ProfileQuestions()]
