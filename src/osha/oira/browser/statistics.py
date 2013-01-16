# -*- coding: utf-8 -*-

import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from AccessControl import Unauthorized
from five import grok

from z3c.saconfig import Session
from zope.sqlalchemy import datamanager
import transaction

from Products.CMFPlone.utils import safe_unicode
import urllib2
from datetime import datetime

logger = logging.getLogger("osha.oira/browser.statistics")

class WriteStatistics(grok.View):

    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')
    grok.name('write-statistics')

    def _walk(self, root, published=False):
        info_surveys = []
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
                        published_date = None
                        if published:
                            if isinstance(survey.published, datetime):
                                published_date = survey.published
                            elif isinstance(survey.published, tuple):
                                published_date = survey.published[2]
                        info_surveys.append((survey_path, survey.Language(),
                            published, published_date, survey.created()))

        return info_surveys

    def render(self):
        urltool = getToolByName(self.context, 'portal_url')
        dbtable_surveys = 'statistics_surveys'

        portal = urltool.getPortalObject()
        # published surveys under /client
        info_surveys_client = self._walk(portal['client'], published=True)
        # unpublished surveys under /sectors
        info_surveys_sectors = self._walk(portal['sectors'], published=False)

        info_surveys = info_surveys_client + info_surveys_sectors

        # write to db
        session = Session()
        session.execute('''DELETE FROM %s;''' % dbtable_surveys)
        def clean(value):
            if isinstance(value, basestring):
                return safe_unicode(value).strip().encode('utf-8')
            return value
        def pg_format(value):
            if value is None:
                return 'NULL'
            if isinstance(value, datetime):
                return "TIMESTAMP '%s'" % value.isoformat()
            return "'%s'" % value
        for line in info_surveys:
            insert = '''INSERT INTO %s VALUES %s;''' % \
                     (dbtable_surveys, '(%s)' % ', '.join(map(pg_format,
                         map(clean,line))))
            session.execute(insert)
        datamanager.mark_changed(session)
        transaction.get().commit()

        from pprint import pformat
        return "Written:\n" + pformat(info_surveys)


class ShowStatistics(grok.View):

    grok.context(IPloneSiteRoot)
    grok.name('show-statistics')

    def render(self):
        ptool = getToolByName(self.context, 'portal_properties')
        site_properties = ptool.site_properties
        URL = site_properties.getProperty('birt_report_url')
        if not URL:
            IStatusMessage(self.request).addStatusMessage(
                    "birt_report_url not set, please contact an administrator",
                    type=u'error')
            return self.request.response.redirect(self.context.absolute_url())
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

        try:
            page = urllib2.urlopen(url)
        except urllib2.URLError:
            IStatusMessage(self.request).addStatusMessage(
                    "Statistics server could not be contacted, please try again later",
                    type=u'error')
            return self.request.response.redirect(self.context.absolute_url())
        self.context.REQUEST.response.setHeader('content-type', page.headers.get('content-type') or 'application/pdf')
        self.context.REQUEST.response.setHeader('content-disposition', page.headers.get('content-disposition') or 'inline; filename="report.pdf"')
        return page.read()
        
        
