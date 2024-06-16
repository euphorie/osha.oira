import logging


log = logging.getLogger(__name__)


def set_up_statistics_db(context):
    log.info(
        "Empty upgrade - statistics database is now handled in "
        "oira.statistics.deployment"
    )
