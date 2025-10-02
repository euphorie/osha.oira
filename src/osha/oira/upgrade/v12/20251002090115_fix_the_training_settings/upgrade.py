from Acquisition import aq_base
from ftw.upgrade import UpgradeStep
from logging import getLogger
from plone import api


logger = getLogger(__name__)


class FixTheTrainingSettings(UpgradeStep):
    """Fix the training settings."""

    def __call__(self):
        # We get the countries that have the training module enabled
        brains = api.content.find(portal_type="euphorie.country")
        countries = (brain.getObject() for brain in brains)
        countries_with_training = (
            country
            for country in countries
            if getattr(aq_base(country), "enable_web_training", False)
        )

        # We get the corresponding client countries paths
        client_paths = []
        for country in countries_with_training:
            brains = api.content.find(
                portal_type="euphorie.clientcountry", getId=country.getId()
            )
            for brain in brains:
                client_paths.append(brain.getPath())

        if not client_paths:
            logger.info("No client countries found for countries with training enabled")
            return

        logger.info(
            "Ensuring web training is enabled for surveys in client countries: %r",
            sorted(client_paths),
        )

        # We get the surveys in those client countries
        brains = api.content.find(path=client_paths, portal_type="euphorie.survey")
        for brain in brains:
            survey = brain.getObject()
            if not getattr(aq_base(survey), "enable_web_training", False):
                logger.info(
                    "Enabling web training for survey %r because its country has the training module enabled",  # noqa: E501
                    survey,
                )
                survey.enable_web_training = True
