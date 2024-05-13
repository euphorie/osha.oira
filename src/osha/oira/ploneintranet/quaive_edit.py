from euphorie.content.browser.country import EditForm as CountryEditForm
from euphorie.content.browser.module import EditForm as ModuleEditForm
from euphorie.content.browser.profilequestion import EditForm as ProfileQuestionEditForm
from osha.oira.content.browser.risk import EditForm as RiskEditForm
from osha.oira.content.browser.sector import EditForm as SectorEditForm
from osha.oira.content.browser.solution import EditForm as SolutionEditForm
from osha.oira.content.browser.survey import EditForm as SurveyEditForm
from plone.dexterity.browser.edit import DefaultEditForm


class QuaiveEditFormMixin:
    @property
    def template(self):
        return self.index

    def nextURL(self):
        return f"{self.context.absolute_url()}/@@{self.__name__}"


class CountryQuaiveEditForm(QuaiveEditFormMixin, CountryEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class ModuleQuaiveEditForm(QuaiveEditFormMixin, ModuleEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class ProfileQuestionQuaiveEditForm(QuaiveEditFormMixin, ProfileQuestionEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class RiskQuaiveEditForm(QuaiveEditFormMixin, RiskEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SectorQuaiveEditForm(QuaiveEditFormMixin, SectorEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SolutionQuaiveEditForm(QuaiveEditFormMixin, SolutionEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SurveyQuaiveEditForm(QuaiveEditFormMixin, SurveyEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SurveyGroupQuaiveEditForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""
