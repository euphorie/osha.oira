from euphorie.client.model import get_current_account
from euphorie.client.model import SurveySession
from osha.oira.client.model import NewsletterSetting
from plone import api
from sqlalchemy import event
from z3c.saconfig import Session

import logging


logger = logging.getLogger(__name__)


def update_user_languages(account_id, tool):
    if not tool:
        return
    if not tool.language:
        logger.info("No language for tool %s", "/".join(tool.getPhysicalPath()))
        return
    language = tool.language.split("-")[0]
    if (
        Session.query(NewsletterSetting.value)
        .filter(NewsletterSetting.account_id == account_id)
        .filter(NewsletterSetting.value == f"language:{language}")
    ).count() == 0:
        Session.add(
            NewsletterSetting(
                account_id=account_id,
                value=f"language:{language}",
            )
        )


@event.listens_for(SurveySession, "init")
def update_user_languages_subscriber(target, args, kwargs):
    if "zodb_path" not in kwargs:
        return
    # kwargs["account_id"] can refer to the account of the session being cloned
    try:
        account = get_current_account()
        if not account:
            return
        client = api.portal.get().client
    except api.exc.CannotGetPortalError:
        # In corner cases (usually unit tests) we may not have a portal.
        # `get_current_account` will then fail, but maybe someone has mocked
        # this call, so we catch the error on a few lines.
        # See https://github.com/euphorie/Euphorie/pull/757
        return
    tool = client.restrictedTraverse(str(kwargs["zodb_path"]), None)
    update_user_languages(account.id, tool)
