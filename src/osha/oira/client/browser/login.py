# coding=utf-8
from ..model import LoginStatistics
from euphorie.client.browser import login
from euphorie.client.model import Account
from z3c.saconfig import Session


class Login(login.Login):
    def login(self, account, remember):
        # Fetch the account again, to circumvent caching
        session = Session()
        account = session.query(Account).filter(Account.id == account.id).one()
        ls = LoginStatistics(account=account)
        account.logins.append(ls)
        return super(Login, self).login(account, remember)
