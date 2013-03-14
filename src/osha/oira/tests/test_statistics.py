from osha.oira.testing import OIRA_INTEGRATION_TESTING
from osha.oira.interfaces import IOSHAContentSkinLayer
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface.declarations import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
import unittest2 as unittest
from Products.statusmessages.adapter import _decodeCookieValue
from euphorie.content.country import ICountry
from euphorie.content.sector import ISector


class TestStatistics(unittest.TestCase):
    """ """
    layer = OIRA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        alsoProvides(self.portal.REQUEST, IOSHAContentSkinLayer)

    def __test_without_server_url(self, context):
        view = getMultiAdapter((context, context.REQUEST),
                               name="show-statistics")

        countries_vocab = getUtility(IVocabularyFactory,
                                     name='osha.oira.countries')(context)
        period_vocab = getUtility(IVocabularyFactory,
                                  name='osha.oira.report_period')(context)
        type_vocab = getUtility(IVocabularyFactory,
                                name='osha.oira.report_type')(context)
        year_vocab = getUtility(IVocabularyFactory,
                                name='osha.oira.report_year')(context)

        for country in countries_vocab._terms:
            for period in period_vocab._terms:
                for rtype in type_vocab._terms:
                    for year in year_vocab._terms:
                        data = {'countries': country.value,
                                'report_period': period.value,
                                'report_type': rtype.value,
                                'tools': 'be/xxxx/xxxx/2010-08-05',
                                'year': year.value
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

    def test_global_statistics(self):
        context = self.portal['sectors']
        self.__test_without_server_url(context)

    def test_country_statistics(self):
        sectors = self.portal['sectors']
        for country in sectors.values():
            if not ICountry.providedBy(country):
                continue
            self.__test_without_server_url(country)

    def test_sector_statistics(self):
        sectors = self.portal['sectors']
        for country in sectors.values():
            if not ICountry.providedBy(country):
                continue
            for sector in country.values():
                if not ISector.providedBy(country):
                    continue
                self.__test_without_server_url(sector)
