# -*- coding: utf-8 -*-
from alchemy_mock.mocking import AlchemyMagicMock
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from alchemy_mock.mocking import UnorderedCall
from euphorie.client import model
from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from osha.oira.statistics.model import SurveySessionStatistics
from osha.oira.statistics.utils import UpdateStatisticsDatabases
from unittest import mock
from unittest import TestCase

import datetime
import sqlalchemy


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


class TestUpdateStatistics(TestCase):
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

    def test_update_assessment(self):
        mock_session_application = StatisticsUnifiedAlchemyMagicMock(
            data=[
                (
                    [
                        mock.call.query(SurveySession, Account),
                        mock.call.filter(
                            SurveySession.id > 1,
                            Account.id == SurveySession.account_id,
                            Account.account_type != "guest",
                        ),
                        mock.call.order_by(SurveySession.id),
                        mock.call.limit(1000),
                        mock.call.offset(0),
                    ],
                    [
                        (
                            SurveySession(
                                id=2,
                                account_id="1",
                                zodb_path="de/test/foo",
                                created=datetime.datetime(
                                    2022, 9, 15, 10, 12, 22, 418958
                                ),
                            ),
                            Account(id=1, account_type="full", created=None),
                        ),
                    ],
                ),
            ]
        )

        updater = UpdateStatisticsDatabases(mock_session_application, "")
        updater.session_statistics = AlchemyMagicMock()
        mock_query = mock.Mock()
        mock_query.first = mock.Mock(return_value=[1])
        updater.session_statistics.query = mock.Mock(return_value=mock_query)
        model.Session = mock_session_application
        updater.update_assessment()

        updater.session_statistics.add_all.assert_called()
        self.assertEqual(updater.session_statistics.add_all.call_args.args[0][0].id, 2)
        self.assertEqual(
            updater.session_statistics.add_all.call_args.args[0][0].tool_path,
            "de/test/foo",
        )
