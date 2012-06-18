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

    def _walk(self, root, published=False):
        info_surveys = []
        info_modules = []
        for country in root.objectValues():
            for sector in country.objectValues():
                for survey_or_group in sector.objectValues():
                    if survey_or_group.portal_type == 'euphorie.survey':
                        surveys = [survey_or_group]
                        survey_parent_path = '/'.join((country.id, sector.id))
                    elif survey_or_group.portal_type == 'euphorie.surveygroup':
                        surveys = survey_or_group.objectValues()
                        survey_parent_path = '/'.join((country.id, sector.id, survey_or_group.id))
                    else:
                        surveys = [] # redundant right now, but in case sth is added below...
                        logger.info('Object is neither survey nor surveygroup, skipping. %s' % '/'.join(survey_or_group.getPhysicalPath()))
                        continue
                    for survey in surveys:
                        survey_path = '/'.join((survey_parent_path, survey.id))
                        if not survey.portal_type == 'euphorie.survey':
                            logger.info('Object is not a survey but inside surveygroup, skipping. %s' % '/'.join(survey.getPhysicalPath()))
                            continue
                        info_surveys.append((survey_path, survey.Language(), published))
                        # we only need modules info for sessions, i.e. published surveys only
                        if published:
                            info_modules = info_modules + map(lambda tup: ('/'.join((survey_parent_path, tup[0])), tup[1]), self._get_modules_info(survey))

        return (info_surveys, info_modules)

    def _get_modules_info(self, obj):
        no_child_risks = 0 #len(obj.objectIds('euphorie.risk'))
        info_child_modules = []
        for module_or_risk in obj.objectValues():
            if module_or_risk.portal_type in ('euphorie.module', 'euphorie.profilequestion'):
                info_child_modules += self._get_modules_info(module_or_risk)
            elif module_or_risk.portal_type == 'euphorie.risk':
                no_child_risks += 1
            else:
                logger.info('Object is neither module nor profile question nor risk, skipping. %s' % '/'.join(module_or_risk.getPhysicalPath()))

        return [(obj.id, no_child_risks)] + map(lambda tup: ('/'.join((obj.id, tup[0])), tup[1]), info_child_modules)

    def render(self):
        urltool = getToolByName(self.context, 'portal_url')
        dbtable_surveys = 'statistics_surveys'
        dbtable_modules = 'statistics_modules'
        path_re = re.compile('/Plone2/[^/]*/(.*)')

        portal = urltool.getPortalObject()
        # published surveys under /client
        info_surveys_client, info_modules_client = self._walk(portal['client'], published=True)
        # unpublished surveys under /sectors
        info_surveys_sectors, info_modules_sectors = self._walk(portal['sectors'], published=False)

        info_surveys = info_surveys_client + info_surveys_sectors
        info_modules = info_modules_client + info_modules_sectors

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
        return "Written:\n" + pformat(info_surveys) + "\n\n" + pformat(info_modules)


class ShowStatistics(grok.View):

    grok.context(IPloneSiteRoot)
    grok.name('show-statistics')

    def render(self):
        ptool = getToolByName(self.context, 'portal_properties')
        site_properties = ptool.site_properties
        URL = site_properties.getProperty('birt_report_url')
        if not URL:
            return "birt_report_url not set, please contact an administrator"
        #URL = 'http://localhost:8080/birt-viewer/frameset?__report=report/OiRA-Reports/usage_statistics.rptdesign&__sessionId=20120131_180440_301&__format=pdf&__pageoverflow=0&__asattachment=true&__overwrite=false'
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized, 'must be logged in to view statistics'
        member = pm.getAuthenticatedMember()
        
        #parsedurl = urlparse.urlparse(URL)
        #parsedquery = urlparse.parse_qs(parsedurl.query)
        #parsedquery['member_id'] = member.id
        #url = urlparse.urlunparse(parsedurl[:4] + (urllib.urlencode(parsedquery),) + parsedurl[5:])
        url = URL + '&sector=%s' % member.id

        page = urllib2.urlopen(url)
        self.context.REQUEST.response.setHeader('content-type', page.headers.get('content-type') or 'application/pdf')
        self.context.REQUEST.response.setHeader('content-disposition', page.headers.get('content-disposition') or 'inline; filename="report.pdf"')
        return page.read()
        
        
