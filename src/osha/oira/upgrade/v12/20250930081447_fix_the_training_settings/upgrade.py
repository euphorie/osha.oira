from Acquisition import aq_base
from ftw.upgrade import UpgradeStep
from logging import getLogger
from plone import api


logger = getLogger(__name__)


class FixTheTrainingSettings(UpgradeStep):
    """Fix the training settings."""

    def __call__(self):
        """Upgrade step to fix the training settings.

        The surveys that had `enable_web_training = True` will be marked as
        `enable_test_questions = True`.

        We will **then** set `enable_web_training = True` for every survey
        whose country has the training module enabled.
        """
        if not api.portal.get_registry_record(
            "euphorie.use_training_module", default=False
        ):
            return

        brains = api.content.find(portal_type="euphorie.survey")
        surveys = [brain.getObject() for brain in brains]

        for survey in surveys:
            if getattr(aq_base(survey), "enable_web_training", False):
                logger.info(
                    "Enabling test questions for survey %r because web training was enabled",  # noqa: E501
                    survey,
                )
                survey.enable_test_questions = True

        brains = api.content.find(
            portal_type=["euphorie.country", "euphorie.clientcountry"]
        )
        countries = [brain.getObject() for brain in brains]

        countries_with_training = []
        for country in countries:
            if getattr(aq_base(country), "enable_web_training", False):
                countries_with_training.append(country)

        for country in countries_with_training:
            brains = api.content.find(context=country, portal_type="euphorie.survey")
            for brain in brains:
                survey = brain.getObject()
                if not getattr(aq_base(survey), "enable_web_training", False):
                    logger.info(
                        "Enabling web training for survey %r because its country %r has the training module enabled",  # noqa: E501
                        survey,
                        country,
                    )
                    survey.enable_web_training = True
