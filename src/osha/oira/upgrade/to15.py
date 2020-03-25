from osha.oira.statistics import model
from sqlalchemy import create_engine


def set_up_statistics_db(context):
    for database in model.STATISTICS_DATABASES:
        database_url = model.get_postgres_url().format(database=database)
        engine = create_engine(database_url)
        model.Base.metadata.create_all(bind=engine, checkfirst=True)
