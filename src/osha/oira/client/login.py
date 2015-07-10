from Acquisition import aq_inner
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from euphorie.client.login import Login as BaseLogin
from euphorie.client.login import Register as BaseRegister
from euphorie.client.login import Reminder as BaseReminder
from euphorie.client.conditions import TermsAndConditions as BaseTermsAndConditions
from .interfaces import IOSHAClientSkinLayer
from .model import LoginStatistics
from osha.oira import _

grok.templatedir("templates")


class Login(BaseLogin):
    grok.layer(IOSHAClientSkinLayer)
    grok.template("login")

    def login(self, account, remember):
        account.logins.append(LoginStatistics(account=account))
        return super(Login, self).login(account, remember)


class LoginForm(Login):
    grok.layer(IOSHAClientSkinLayer)
    grok.name("login_form")
    grok.template("login_form")


class Register(BaseRegister):
    grok.layer(IOSHAClientSkinLayer)
    grok.template("register")


class TermsAndConditions(BaseTermsAndConditions):
    grok.name("terms-and-conditions")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("conditions")


class Reminder(BaseReminder):
    grok.layer(IOSHAClientSkinLayer)
    grok.name("reminder")
    grok.template("reminder")

    def update(self):
        context = aq_inner(self.context)
        self.back_url = self.request.form.get("came_from")
        if not self.back_url:
            self.back_url = context.absolute_url()

        if self.request.environ["REQUEST_METHOD"] == "POST":
            if self.request.form.get('cancel', ''):
                self.request.response.redirect(self.back_url)
            if self._sendReminder():
                flash = IStatusMessage(self.request).addStatusMessage
                flash(_(u"An email with a password reminder has been "
                        u"sent to your address."), "notice")
                self.request.response.redirect(self.back_url)
