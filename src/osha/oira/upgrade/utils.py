from alembic import command
from alembic import op
from alembic.config import Config
from euphorie.client.model import Session
from logging import getLogger
from osha.oira.statistics.model import get_postgres_url
from osha.oira.statistics.model import STATISTICS_DATABASE_PATTERN
from osha.oira.statistics.utils import list_countries
from pkg_resources import resource_filename
from sqlalchemy import inspect


logger = getLogger(__name__)


def has_table(name):
    """Utility function that can be used in alembic upgrades to check if a
    table exists."""
    return name in inspect(op.get_bind()).get_table_names()


def has_column(table_name, column_name):
    """Utility function that can be used in alembic upgrades to check if a
    column exists."""
    bind = op.get_bind()
    columns = inspect(bind).get_columns(table_name)
    return any(column["name"] == column_name for column in columns)


def alembic_upgrade_to(revision):
    script_location = resource_filename("osha.oira.upgrade", "alembic")
    url = Session().bind.engine.url.__to_string__(hide_password=False)
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    try:
        command.upgrade(alembic_cfg, revision)
    except Exception:
        logger.exception(
            "Migration failed, you might need to adapt the script to match "
            "your DB state"
        )


def alembic_upgrade_statistics_to(revision):
    script_location = resource_filename("osha.oira.upgrade", "alembic_statistics")
    countries = ["global"] + list_countries(Session())
    url_base = get_postgres_url()
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("databases", ",".join(countries))
    for country in countries:
        url = url_base.format(
            database=STATISTICS_DATABASE_PATTERN.format(suffix=country)
        )
        alembic_cfg.set_section_option(country, "sqlalchemy.url", url)
    try:
        command.upgrade(alembic_cfg, revision)
    except Exception:
        logger.exception(
            "Migration failed, you might need to adapt the script to match "
            "your DB state"
        )
