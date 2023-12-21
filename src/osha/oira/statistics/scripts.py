from euphorie.client import model
from osha.oira.statistics.model import create_session
from osha.oira.statistics.utils import UpdateStatisticsDatabases

import argparse
import datetime
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
        "--since",
        type=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"),
        help=(
            "Start date for statistics update. Entries newer than this date will be "
            "synchronized. Can only be used to specify dates earlier than the default "
            "to prevent gaps in the data. "
            "Default is latest entry date in statistics database."
        ),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help=("How many rows to process in one go before committing to the database"),
    )
    parser.add_argument(
        "--optimize-cp-query",
        action="store_true",
        help=(
            "Use separate query for calculating completion percentage instead of "
            "method on session object. Faster when updating a lot of sessions."
        ),
    )
    args = parser.parse_args()
    log.info("Updating statistics databases")
    session_application = create_session(args.src)

    # XXX Patching Session because otherwise completion_percentage fails with
    # zope.interface.interfaces.ComponentLookupError:
    # (<InterfaceClass z3c.saconfig.interfaces.IScopedSession>, '')
    model.Session = session_application

    update_db = UpdateStatisticsDatabases(
        session_application,
        args.dst,
        since=args.since,
        b_size=args.batch_size,
        optimize_cp_query=args.optimize_cp_query,
    )
    output = update_db()
    if "OK" not in output:
        sys.exit(1)
