# -*- coding: utf-8 -*-

import logging
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from z3c.saconfig import Session
from zope.sqlalchemy import datamanager
import transaction

from Products.CMFPlone.utils import safe_unicode
import re

logger = logging.getLogger("osha.oira/browser.statistics")

class WriteStatistics(BrowserView):

    def __init__(self, request, context):
        super(BrowserView, self).__init__(request, context)

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        dbtable_surveys = 'statistics_surveys'
        dbtable_modules = 'statistics_modules'
        path_re = re.compile('/Plone2/[^/]*/(.*)')

        import ipdb; ipdb.set_trace()
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
