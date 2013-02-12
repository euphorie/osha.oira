from zope import schema
from zope.interface import directlyProvides
from sqlalchemy.orm import object_session
from AccessControl import getSecurityManager
from five import grok
from z3c.form import button
from plone.directives import form
from Products.statusmessages.interfaces import IStatusMessage
from euphorie.client.country import View as EuphorieView
from euphorie.client.country import IClientCountry
from euphorie.client.model import SurveySession
from .interfaces import IOSHAClientSkinLayer
from .. import _


grok.templatedir("templates")


class View(EuphorieView):
    grok.layer(IOSHAClientSkinLayer)
    grok.template("sessions")


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
