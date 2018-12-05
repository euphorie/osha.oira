# coding=utf-8
from euphorie.client.browser import login
from ..model import LoginStatistics


class LoginForm(login.LoginForm):

    def login(self, account, remember):
        ls = LoginStatistics(account=account)
        account.logins.append(ls)
        return super(LoginForm, self).login(account, remember)
