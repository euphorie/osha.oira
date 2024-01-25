from collections import defaultdict
from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from ftw.upgrade import UpgradeStep
from osha.oira.client.subscribers import update_user_languages
from plone import api
from plone.memoize.view import memoize
from z3c.saconfig import Session

import logging


logger = logging.getLogger(__name__)


class SetNewsletterLanguagesPerUser(UpgradeStep):
    """Set newsletter languages per user."""

    @property
    @memoize
    def client(self):
        return api.portal.get().client

    @memoize
    def get_tool(self, zodb_path):
        tool = self.client.restrictedTraverse(zodb_path, None)
        if not tool:
            return None
        if not tool.language:
            logger.info("No language for tool %s", zodb_path)
            return None
        return tool

    def __call__(self):
        sessions = (
            Session.query(SurveySession, Account)
            .filter(SurveySession.account_id == Account.id)
            .filter(Account.account_type != "guest")
            .filter(SurveySession.archived.is_(None))
        )
        done = defaultdict(list)
        for session, account in sessions:
            if session.zodb_path in done[account.id]:
                continue
            tool = self.get_tool(session.zodb_path)
            if not tool:
                continue
            update_user_languages(account.id, tool)
            done[account.id].append(session.zodb_path)
