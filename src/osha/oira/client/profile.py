from five import grok
from euphorie.client import profile
from euphorie.content.profilequestion import IProfileQuestion
from .interfaces import IOSHAClientSkinLayer
from .. import _

grok.templatedir("templates")


def _questions(context):
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
            for child in context.ProfileQuestions()]


class OSHAProfile(profile.Profile):
    """ Override the original profile to provide our own template.
    """
    grok.layer(IOSHAClientSkinLayer)
    grok.template("profile")
    grok.name("profile")

    def ProfileQuestions(self):
        return _questions(self.context)

    def getDesiredProfile(self):
        """Get the requested profile from the request.

        The profile is returned as a dictionary. The id of the profile
        questions are used as keys. For optional profile questions the value is
        a boolean.  For repetable profile questions the value is a list of
        titles as provided by the user. This format is compatible with
        :py:func:`extractProfile`.

        :rtype: dictionary with profile answers
        """
        profile = {}
        for (id, answer) in self.request.form.items():
            question = self.context.get(id)
            if not IProfileQuestion.providedBy(question):
                continue
            if not self.request.get("pq{0}.present".format(id), '') == 'yes':
                continue
            if isinstance(answer, list):
                profile[id] = filter(None, (a.strip() for a in answer))
                if not self.request.get("pq{0}.multiple".format(id), '') == 'yes':
                    profile[id] = profile[id][:1]
            else:
                profile[id] = answer
        return profile


class OSHAUpdate(OSHAProfile, profile.Update):
    """ Override the original profile to provide our own template.
    """
    grok.layer(IOSHAClientSkinLayer)
    grok.template('update')
    grok.name('update')
