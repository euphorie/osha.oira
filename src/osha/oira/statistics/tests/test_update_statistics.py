from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from alchemy_mock.mocking import UnorderedCall
from datetime import datetime
from euphorie.client.model import Account
from osha.oira.statistics.model import AccountStatistics
from osha.oira.statistics.utils import UpdateStatisticsDatabases
from unittest import mock

import sqlalchemy
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
    def test_update_account_empty(self):
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
        updater.session_statistics = StatisticsUnifiedAlchemyMagicMock()
        updater.update_account()

        updater.session_statistics.add.assert_called()
        self.assertEqual(updater.session_statistics.add.call_args.args[0].id, 1)
        self.assertEqual(
            updater.session_statistics.add.call_args.args[0].account_type, "full"
        )

    def test_update_account_already_up_to_date(self):
        mock_session_application = StatisticsUnifiedAlchemyMagicMock()

        updater = UpdateStatisticsDatabases(mock_session_application, "")
        updater.session_statistics = StatisticsUnifiedAlchemyMagicMock(
            data=[
                (
                    [
                        mock.call.query(
                            sqlalchemy.func.max(AccountStatistics.creation_date)
                        ),
                    ],
                    [[datetime.now()]],
                ),
            ]
        )
        updater.update_account()
        updater.session_statistics.add.assert_not_called()
