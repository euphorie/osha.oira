# -*- coding: utf-8 -*-

import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from AccessControl import Unauthorized
from five import grok

from z3c.saconfig import Session
from zope.sqlalchemy import datamanager
import transaction

from Products.CMFPlone.utils import safe_unicode
import re
import urlparse, urllib, urllib2

logger = logging.getLogger("osha.oira/browser.statistics")

class WriteStatistics(grok.View):

    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')
    grok.name('write-statistics')

    def render(self):
        cat = getToolByName(self.context, 'portal_catalog')
        dbtable_surveys = 'statistics_surveys'
        dbtable_modules = 'statistics_modules'
        path_re = re.compile('/Plone2/[^/]*/(.*)')

        published_surveys = cat(portal_type='euphorie.survey',path='/Plone2/client',sort_on='path')
        unpublished_surveys = cat(portal_type='euphorie.survey',path='/Plone2/sectors',sort_on='path')
        modules = cat(portal_type='euphorie.module',sort_on='path')

        # gather info
        # path, Language, published
        info_surveys = [(path_re.match(br.getPath()).group(1),
                 br.getObject().Language(),
                 #len(cat(portal_type='euphorie.risk', path=br.getPath())),
                 True) for br in published_surveys]
        info_surveys = info_surveys + [(path_re.match(br.getPath()).group(1),
                 br.getObject().Language(),
                 #len(cat(portal_type='euphorie.risk', path=br.getPath())),
                 False) for br in unpublished_surveys]
        # path, number of risks
        info_modules = [(path_re.match(br.getPath()).group(1),
                 len(cat(portal_type='euphorie.risk', path=br.getPath()))) for br in modules]

        # write to db
        session = Session()
        session.execute('''DELETE FROM %s;''' % dbtable_surveys)
        session.execute('''DELETE FROM %s;''' % dbtable_modules)
        def clean(value):
            if isinstance(value, basestring):
                return safe_unicode(value).strip().encode('utf-8')
            return value
        for line in info_surveys:
            insert = '''INSERT INTO %s VALUES %s;''' % \
                     (dbtable_surveys, str(tuple(map(clean,line))))
            session.execute(insert)
        for line in info_modules:
            insert = '''INSERT INTO %s VALUES %s;''' % \
                     (dbtable_modules, str(tuple(line)))
            session.execute(insert)
        datamanager.mark_changed(session)
        transaction.get().commit()

        from pprint import pformat
        return "Written:\n" + pformat(info_surveys) + pformat(info_modules)


class ShowStatistics(grok.View):

    grok.context(IPloneSiteRoot)
    grok.name('show-statistics')

    def render(self):
        URL = 'http://birt.osha.europa.eu/birt-viewer/frameset?__report=linkstats/linkreportdirect.rptdesign&State=orange%20%20%20%20&ContentType=Document&Category=.%2A&Path=/&Subsite=main'
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized, 'must be logged in to view statistics'
        member = pm.getAuthenticatedMember()
        
        #parsedurl = urlparse.urlparse(URL)
        #parsedquery = urlparse.parse_qs(parsedurl.query)
        #parsedquery['member_id'] = member.id
        #url = urlparse.urlunparse(parsedurl[:4] + (urllib.urlencode(parsedquery),) + parsedurl[5:])
        url = URL + '&member_id=%s' % member.id

        page = urllib2.urlopen(url)
        return page.read()
        
        
