# coding=utf-8
from euphorie.client.browser import login
from ..model import LoginStatistics


class LoginForm(login.LoginForm):

    def login(self, account, remember):
        account.logins.append(LoginStatistics(account=account))
        return super(LoginForm, self).login(account, remember)
