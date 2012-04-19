from five import grok
from euphorie.client import login as register
from plonetheme.nuplone.skin import login
from osha.oira.interfaces import IOSHAClientSkinLayer
from osha.oira.interfaces import IOSHAContentSkinLayer

from AccessControl import getSecurityManager
from z3c.saconfig import Session
from zope.sqlalchemy import datamanager
import transaction

grok.templatedir("templates")

class Register(register.Register):
    grok.require("zope2.View")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("register")
    
class Login(login.Login):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("login")

    def update(self):
        super(Login, self).update()
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

