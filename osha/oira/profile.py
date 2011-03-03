from Acquisition import aq_inner
from five import grok
from z3c.saconfig import Session
from euphorie.client.session import SessionManager
from euphorie.content.survey import ISurvey
from euphorie.client.utils import RelativePath
from euphorie.client import profile
from osha.oira import interfaces

class OSHAUpdate(profile.Update):
    """ Override to add fix for #2583
        The sessiontree is not correctly being updated when it's
        different/outdated compared to a newly published survey.
    """
    grok.context(ISurvey)
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.name("update")
    
    def setupSession(self, force_new_session=False):
        """ Copied over from euphorie.client.profile..py Profile

            Setup the session for the context survey. This will rebuild the
            session tree if the profile has changed.
        """
        survey=aq_inner(self.context)
        new_profile=self.getDesiredProfile()

        if not self.session.hasTree():
            profile.BuildSurveyTree(survey, new_profile, dbsession=self.session)
        else:
            # This is the fix... we force the session to be updated.
            if self.current_profile!=new_profile or force_new_session:
                old_session=self.session
                new_session=SessionManager.start(old_session.title, survey)
                profile.BuildSurveyTree(survey, new_profile, new_session)
                new_session.copySessionData(old_session)
                Session.delete(old_session)
                self.session=new_session
            else:
                self.session.touch()

    def update(self):
        survey=aq_inner(self.context)
        self.profile_questions=self.ProfileQuestions()
        self.session=SessionManager.session
        self.current_profile=profile.extractProfile(survey)
        assert self.session is not None
        assert self.session.zodb_path==RelativePath(self.request.client, aq_inner(self.context))
        
        if not self.profile_questions or self.request.environ["REQUEST_METHOD"]=="POST":
            # This is the fix... we force the session to be updated.
            self.setupSession(force_new_session=True)
            self.request.response.redirect(survey.absolute_url()+"/identification")


