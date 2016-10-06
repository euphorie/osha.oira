# coding=utf-8
from five import grok
from euphorie.client.login import Login as BaseLogin
from euphorie.client.conditions import TermsAndConditions as BaseTermsAndConditions  # noqa
from .interfaces import IOSHAClientSkinLayer
from .model import LoginStatistics

grok.templatedir("templates")


class Login(BaseLogin):
    grok.layer(IOSHAClientSkinLayer)

    def login(self, account, remember):
        account.logins.append(LoginStatistics(account=account))
        return super(Login, self).login(account, remember)


class TermsAndConditions(BaseTermsAndConditions):
    grok.name("terms-and-conditions")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("conditions")
