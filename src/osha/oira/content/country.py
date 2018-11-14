# coding=utf-8
from euphorie.content.country import ManageUsers
from five import grok
from osha.oira.interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class OSHAManageUsers(ManageUsers):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("user_mgmt")
