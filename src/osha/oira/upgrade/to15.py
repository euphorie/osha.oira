from euphorie.client.model import Session as EuphorieSession
from osha.oira.statistics import model
from osha.oira.statistics.utils import list_statistics_databases
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

import logging


log = logging.getLogger(__name__)


def set_up_statistics_db(context):
    for database in list_statistics_databases(EuphorieSession):
        database_url = model.get_postgres_url().format(database=database)
        engine = create_engine(database_url)
        try:
            model.Base.metadata.create_all(bind=engine, checkfirst=True)
        except SQLAlchemyError as e:
            log.warn(f"Could not set up {database}: {e}")
