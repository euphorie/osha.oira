# -*- coding: utf-8 -*-
from osha.oira.statistics.model import create_session
from osha.oira.statistics.utils import UpdateStatisticsDatabases

import argparse
import logging
import sys


log = logging.getLogger(__name__)


def update_statistics():
    logging.basicConfig(stream=sys.stderr, level=0)
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
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help=("How many rows to process in one go before committing to the database"),
    )
    args = parser.parse_args()
    log.info("Updating statistics databases")
    session_application = create_session(args.src)
    update_db = UpdateStatisticsDatabases(
        session_application, args.dst, b_size=args.batch_size
    )
    update_db()
