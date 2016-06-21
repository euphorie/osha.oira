from Products.statusmessages.adapter import _decodeCookieValue
from euphorie.content.country import ICountry
from euphorie.content.sector import ISector
from osha.oira.interfaces import IOSHAContentSkinLayer
from osha.oira.testing import OIRA_INTEGRATION_TESTING
from plone import api
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface.declarations import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from osha.oira.content import statistics
from osha.oira.content.statistics import ReportPeriod
import unittest2 as unittest


class TestStatistics(unittest.TestCase):
    """ """
    layer = OIRA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        alsoProvides(self.portal.REQUEST, IOSHAContentSkinLayer)
        # Clear the birt_report_url property if it exists

    def __test_stats_url(self, context, country, period, year, rtype, format):
        tool = 'be/xxxx/xxxx/2010-08-05'
        view = getMultiAdapter((context, context.REQUEST),
                               name="show-statistics")
        report_period = ReportPeriod({
            'year': year,
            'period': period
        })
        data = {'countries': country,
                'report_period': report_period,
                'report_type': rtype,
                'tools': tool,
                'file_format': format,
                }
        # Without setting the statistics server URL in
        # site_props, the return url must be None
        url = view.getStatisticsServerURL(data)
        cookies = context.REQUEST.RESPONSE.cookies
        self.assertIsNone(url)
        self.assertTrue('statusmessages' in cookies)
        cookie = cookies.get('statusmessages')
        message = _decodeCookieValue(cookie['value'])[0]
        self.assertEqual(
            message.message,
            u'birt_report_url not set, please contact '
            u'an administrator'
        )
        self.assertEqual(message.type, u'error')

        # Now set the statistics server URL and test
        sprops = api.portal.get_tool(
            name='portal_properties').site_properties

        server_url = 'http://localhost'
        sprops._setProperty('birt_report_url',
                            server_url)
        url = view.getStatisticsServerURL(data)
        month = 0
        quarter = 0
        if period > 12:
            quarter = period % 12
        else:
            month = period
        filename = statistics.StatisticsMixin.filename[rtype]

        # Ugly but I'm in a rush
        test_url = "&".join([
            server_url,
            '__report=statistics/%s' % filename,
            rtype == 'country' and 'country=%s' % country or
            rtype == 'tool' and 'tool=%s' % tool or
            'sector=%25',
            'year=%d' % year,
            'month=%d' % month,
            'quarter=%d' % quarter,
            'testsessions=0',
            '__format=%s' % format
        ])
        self.assertEqual(url, test_url)
        sprops._delProperty('birt_report_url')

    def __test(self, context):
        countries_vocab = getUtility(IVocabularyFactory,
                                     name='osha.oira.countries')(context)
        period_vocab = getUtility(IVocabularyFactory,
                                  name='osha.oira.report_period')(context)
        type_vocab = getUtility(IVocabularyFactory,
                                name='osha.oira.report_type')(context)
        year_vocab = getUtility(IVocabularyFactory,
                                name='osha.oira.report_year')(context)
        file_format = getUtility(IVocabularyFactory,
                                 name='osha.oira.report_file_format')(context)
        for country in countries_vocab._terms:
            for period in period_vocab._terms:
                for rtype in type_vocab._terms:
                    for year in year_vocab._terms:
                        for format in file_format._terms:
                            self.__test_stats_url(context,
                                                  country.value,
                                                  period.value,
                                                  year.value,
                                                  rtype.value,
                                                  format.value)

    def test_global_statistics(self):
        context = self.portal['sectors']
        self.__test(context)

    def test_country_statistics(self):
        sectors = self.portal['sectors']
        for country in sectors.values():
            if not ICountry.providedBy(country):
                continue
            self.__test(country)

    def test_sector_statistics(self):
        sectors = self.portal['sectors']
        for country in sectors.values():
            if not ICountry.providedBy(country):
                continue
            for sector in country.values():
                if not ISector.providedBy(country):
                    continue
                self.__test(sector)

