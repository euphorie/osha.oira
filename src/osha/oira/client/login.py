# coding=utf-8
from five import grok
from euphorie.client import login
from euphorie.client.conditions import TermsAndConditions as BaseTermsAndConditions  # noqa
from .interfaces import IOSHAClientSkinLayer
from .model import LoginStatistics

grok.templatedir("templates")


class LoginForm(login.LoginForm):
    grok.layer(IOSHAClientSkinLayer)

    def login(self, account, remember):
        account.logins.append(LoginStatistics(account=account))
        return super(LoginForm, self).login(account, remember)


class TermsAndConditions(BaseTermsAndConditions):
    grok.name("terms-and-conditions")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("conditions")
