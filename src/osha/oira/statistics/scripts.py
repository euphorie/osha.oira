# -*- coding: utf-8 -*-
from osha.oira.statistics.model import create_session
from osha.oira.statistics.utils import UpdateStatisticsDatabases
import argparse
import logging

log = logging.getLogger(__name__)


def update_statistics():
    parser = argparse.ArgumentParser(
        description=(
            "Update the statistics databases from the main OiRA application database. "
        )
    )
    parser.add_argument(
        "--src",
        type=str,
        required=True,
        help=(
            "Connection string to the source database (main OiRA application "
            "database). Example: postgres://XXXX:XXXX@localhost/euphorie"
        ),
    )
    parser.add_argument(
        "--dst",
        type=str,
        required=True,
        help=(
            "Connection string to the destination databases (dedicated statistics "
            "databases). The placeholder {database} will be replaced with the database "
            "name. Example: postgres://XXXX:XXXX@localhost/{database}"
        ),
    )
    args = parser.parse_args()
    log.info("Updating statistics databases")
    session_application = create_session(args.src)
    update_db = UpdateStatisticsDatabases(session_application, args.dst)
    update_db()
