# coding=utf-8
from euphorie.client import model
from pkg_resources import resource_filename
from Zope2.App import zcml
from z3c.saconfig import Session

import logging
import sys

logging.basicConfig()
logger = logging.getLogger(__name__)
stdout = logging.StreamHandler(sys.stdout)
stderr = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s",
    "%Y-%m-%d %H:%M:%S"
)
stdout.setFormatter(formatter)
stdout.setLevel(logging.INFO)
logger.addHandler(stdout)
stderr.setFormatter(formatter)
stderr.setLevel(logging.ERROR)
logger.addHandler(stderr)

if sys.argv[0].endswith("/bin/test"):
    config = resource_filename("euphorie.client.tests", "configure.zcml")
else:
    config = "parts/instance/etc/package-includes/999-additional-overrides.zcml"  # noqa: E501

zcml.load_config(config)
model.metadata.create_all(Session.bind, checkfirst=True)
session = Session()


class CleanUpGuestSessions(object):

    sql = """
WITH old_guest_sessions AS (
    SELECT session.id, count(tree.id) AS num_risks
    FROM account, session LEFT JOIN tree
    ON session.id = tree.session_id
    WHERE session.account_id = account.id
      AND account.account_type = 'guest'
      AND session.created < current_date - interval '1 week'
    GROUP BY session.id
)
DELETE FROM session USING old_guest_sessions
WHERE old_guest_sessions.id = session.id
  AND old_guest_sessions.num_risks = 0;

WITH guest_accounts AS (
    SELECT account.id, loginname, count(session.id) AS num_sessions
    FROM account LEFT JOIN session
    ON account.id = session.account_id OR account.id = session.last_modifier_id
    WHERE account_type = 'guest' GROUP BY account.id
)
DELETE FROM account USING guest_accounts
WHERE guest_accounts.id = account.id
  AND guest_accounts.num_sessions = 0;
"""

    def __call__(self):
        session.execute("BEGIN;")
        count_sql = "select count(*) from account where account_type = 'guest'"
        old_count = session.execute(count_sql).first()
        logger.warning(f"Current number of test sessions: {old_count[0]}")
        session.execute(self.sql)
        session.execute("COMMIT;")
        new_count = session.execute(count_sql).first()
        logger.warning(f"New number of test sessions: {new_count[0]}")


clean_up_guest_sessions = CleanUpGuestSessions()
