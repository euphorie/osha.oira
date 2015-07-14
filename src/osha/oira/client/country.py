import urllib
from zope import schema
from zope.interface import directlyProvides
from sqlalchemy.orm import object_session
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from five import grok
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from euphorie.client import utils
from euphorie.client.country import DeleteSession as EuphorieDeleteSession
from euphorie.client.country import View as EuphorieView
from euphorie.client.country import IClientCountry
from euphorie.client.login import Tryout
from euphorie.client.model import SurveySession
from .interfaces import IOSHAClientSkinLayer
from z3c.saconfig import Session
from zope.interface import Interface
from .. import _


grok.templatedir("templates")


class View(EuphorieView):
    grok.layer(IOSHAClientSkinLayer)
    grok.template("sessions")


class CreateSession(View):
    grok.context(Interface)
    grok.name("new-session.html")
    grok.template("new-session")


class CreateTestSession(View, Tryout):
    grok.context(Interface)
    grok.require("zope2.View")
    grok.name("new-session-test.html")
    grok.template("new-session-test")

    def update(self):
        context = aq_inner(self.context)
        came_from = self.request.form.get("came_from")
        if came_from:
            if isinstance(came_from, list):
                # If came_from is both in the querystring and the form data
                came_from = came_from[0]
        else:
            came_from = context.absolute_url()
        self.register_url = "%s/@@register?%s" % (
            context.absolute_url(), urllib.urlencode({'came_from': came_from}))
        utils.setLanguage(self.request, self.context)
        if self.request.environ["REQUEST_METHOD"] == "POST":
            reply = self.request.form
            if reply["action"] == "new":
                account = self.createGuestAccount()
                self.login(account, False)
                self._NewSurvey(reply, account)
        self._updateSurveys()


class ConfirmationDeleteSession(grok.View):
    grok.context(IClientCountry)
    grok.name("confirmation-delete-session.html")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("confirmation-delete-session")

    def __call__(self, *args, **kwargs):
        try:
            self.session_id = int(self.request.get("id"))
        except (ValueError, TypeError):
            raise KeyError("Invalid session id")
        user = getSecurityManager().getUser()
        session = object_session(user).query(SurveySession)\
                .filter(SurveySession.account == user)\
                .filter(SurveySession.id == self.session_id).first()
        if session is None:
            raise KeyError("Unknown session id")
        self.session_title = session.title
        return super(ConfirmationDeleteSession, self).__call__(*args, **kwargs)


class DeleteSession(EuphorieDeleteSession):
    grok.layer(IOSHAClientSkinLayer)
    grok.name("delete-session")

    def render(self):
        session = Session()
        ss = session.query(SurveySession).get(self.request.form["id"])
        if ss is not None:
            flash = IStatusMessage(self.request).addStatusMessage
            flash(_(u"Session `${name}` has been deleted.",
                    mapping={"name": getattr(ss, 'title')}), "success")
            session.delete(ss)
        self.request.response.redirect(self.context.absolute_url())


class RenameSessionSchema(form.Schema):
    title = schema.TextLine(required=False)


class RenameSession(form.SchemaForm):
    grok.context(IClientCountry)
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(IOSHAClientSkinLayer)
    grok.name("rename-session")
    grok.template("rename-session")
    form.wrap(False)

    schema = RenameSessionSchema

    def getContent(self):
        try:
            session_id = int(self.request.get("id"))
        except (ValueError, TypeError):
            raise KeyError("Invalid session id")
        user = getSecurityManager().getUser()
        session = object_session(user).query(SurveySession)\
                .filter(SurveySession.account == user)\
                .filter(SurveySession.id == session_id).first()
        if session is None:
            raise KeyError("Unknown session id")
        self.original_title = session.title
        directlyProvides(session, RenameSessionSchema)
        return session

    @button.buttonAndHandler(_(u"Save"))
    def handleSave(self, action):
        (data, errors) = self.extractData()
        if errors:
            return
        if data["title"]:
            flash = IStatusMessage(self.request).addStatusMessage
            self.getContent().title = data['title']
            flash(_(u"Session title has been changed to ${name}",
                mapping={"name": data["title"]}), "success")
        self.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        self.response.redirect(self.context.absolute_url())
