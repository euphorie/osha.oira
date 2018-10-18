# coding=utf-8
from plone import api
from Products.CMFPlone.utils import get_installer


def install_pas_plugins_ldap(context):
    qi = get_installer(api.portal.get())
    if not qi.is_product_installed('pas.plugins.ldap'):
        qi.install_product('pas.plugins.ldap')
