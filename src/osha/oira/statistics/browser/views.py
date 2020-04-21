# -*- coding: utf-8 -*-
from euphorie.client.model import Session as EuphorieSession
from osha.oira.statistics.model import get_postgres_url
from osha.oira.statistics.utils import UpdateStatisticsDatabases
from Products.Five import BrowserView
import logging

log = logging.getLogger(__name__)


class UpdateStatistics(BrowserView):
    def get_postgres_url(self):
        return get_postgres_url()

    def __call__(self):
        log.info("Updating statistics databases")
        postgres_url = self.get_postgres_url()
        if postgres_url is None:
            return "Could not get postgres connection URL!"
        update_db = UpdateStatisticsDatabases(EuphorieSession, postgres_url)
        update_db()
        log.info("Done")
        return "Done"
