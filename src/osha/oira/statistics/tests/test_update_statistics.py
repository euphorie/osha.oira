from alchemy_mock.mocking import AlchemyMagicMock
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from alchemy_mock.mocking import UnorderedCall
from euphorie.client.model import Account
from osha.oira.statistics.utils import UpdateStatisticsDatabases
from unittest import mock

import unittest


class StatisticsUnifiedAlchemyMagicMock(UnifiedAlchemyMagicMock):
    unify = {
        "query": None,
        "add_columns": None,
        "join": None,
        "options": None,
        "group_by": None,
        "filter": UnorderedCall,
        "filter_by": UnorderedCall,
        "order_by": None,
        "offset": None,  # This is missing in UnifiedAlchemyMagicMock
        "limit": None,
        "distinct": None,
    }


class TestUpdateStatistics(unittest.TestCase):
    @unittest.skip(
        "Fails with: TypeError: '>' not supported between instances of 'AlchemyMagicMock' and 'datetime.datetime'"  # noqa: E501
    )
    def test_update_account(self):
        mock_session_application = StatisticsUnifiedAlchemyMagicMock(
            data=[
                (
                    [
                        mock.call.query(Account),
                        mock.call.order_by(Account.id),
                        mock.call.limit(1000),
                        mock.call.offset(0),
                    ],
                    [Account(id=1, account_type="full", created=None)],
                ),
            ]
        )

        updater = UpdateStatisticsDatabases(mock_session_application, "")
        updater.session_statistics = AlchemyMagicMock()
        updater.update_account()

        updater.session_statistics.add_all.assert_called()
        self.assertEqual(updater.session_statistics.add_all.call_args.args[0][0].id, 1)
        self.assertEqual(
            updater.session_statistics.add_all.call_args.args[0][0].account_type, "full"
        )
