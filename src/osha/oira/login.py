from five import grok
from euphorie.client import login
from osha.oira.interfaces import IOSHAClientSkinLayer

from AccessControl import getSecurityManager
from z3c.saconfig import Session
from zope.sqlalchemy import datamanager
import transaction

grok.templatedir("templates")

class Register(login.Register):
    grok.require("zope2.View")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("register")
    
class LoginView(login.LoginView):
    #grok.require("zope2.View")
    #grok.layer(IOSHAClientSkinLayer)

    def update(self):
        super(LoginView, self).update()
        member = getSecurityManager().getUser()
        if not member.getId():
            return
        session = Session()
        select = 'SELECT id FROM account WHERE loginname = \'%s\';' % member.getId()
        res = session.execute(select).fetchall()
        account_id = None
        if len(res) > 0 and res[0]:
            account_id = res[0][0]
        if not account_id:
            return
        insert = '''INSERT INTO statistics_login VALUES (default, %s, now());''' % account_id
        session.execute(insert)
        datamanager.mark_changed(session)
        transaction.get().commit()
        return

