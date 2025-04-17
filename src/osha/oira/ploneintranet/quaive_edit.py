from euphorie.content.browser.country import EditForm as CountryEditForm
from euphorie.content.browser.module import EditForm as ModuleEditForm
from euphorie.content.browser.profilequestion import EditForm as ProfileQuestionEditForm
from osha.oira import _
from osha.oira.content.browser.risk import EditForm as RiskEditForm
from osha.oira.content.browser.sector import EditForm as SectorEditForm
from osha.oira.content.browser.solution import EditForm as SolutionEditForm
from osha.oira.content.browser.survey import EditForm as SurveyEditForm
from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin
from plone.dexterity.browser.edit import DefaultEditForm
from z3c.form.field import Field
from zope import schema


class CountryQuaiveEditForm(QuaiveEditFormMixin, CountryEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class ModuleQuaiveEditForm(QuaiveEditFormMixin, ModuleEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class ProfileQuestionQuaiveEditForm(QuaiveEditFormMixin, ProfileQuestionEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class TrainingQuestionQuaiveEditForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class RiskQuaiveEditForm(QuaiveEditFormMixin, RiskEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SectorQuaiveEditForm(QuaiveEditFormMixin, SectorEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SolutionQuaiveEditForm(QuaiveEditFormMixin, SolutionEditForm):
    """Custom edit form designed to be embedded in Quaive"""


class SurveyQuaiveEditForm(QuaiveEditFormMixin, SurveyEditForm):
    """Custom edit form designed to be embedded in Quaive"""

    label = _("Configuration")

    def updateFields(self):
        """Add an additional tool_title field to configure the survey title."""
        super().updateFields()

        # Do not show the field to update the title
        self.fields = self.fields.omit("title")

        # Add a new Text field to update the survey title
        tool_title_field = Field(
            schema.TextLine(
                title=_("label_title", default="Title"),
                description=_(
                    "help_tool_title_field",
                    default="This will change the title of this survey.",
                ),
                required=True,
                default=self.context.aq_parent.title,
            ),
            name="tool_title",
            ignoreContext=True,
        )

        tool_obsolete_field = Field(
            schema.Bool(
                title=_("label_tool_obsolete_field", default="Obsolete OiRA Tool"),
                description=_(
                    "help_tool_obsolete_field",
                    default="Mark this survey as obsolete.",
                ),
                required=False,
                default=self.context.aq_parent.obsolete,
            ),
            name="tool_obsolete",
            ignoreContext=True,
        )

        # Before adding the new fields, we use the existing fields keys to
        # build an ordered list
        sorted_keys = ["tool_title"] + list(self.fields) + ["tool_obsolete"]

        # Append the new fields to the existing fields
        self.fields.update(
            {"tool_title": tool_title_field, "tool_obsolete": tool_obsolete_field}
        )

        # Reorder the fields to put the new fields at the top
        self.fields = self.fields.select(*sorted_keys)

    def applyChanges(self, data):
        """This additionally updates attributes on the parent surveygroup (the tool)."""
        tool = self.context.aq_parent
        marker = object()

        tool_changed = False
        tool_title = data.get("tool_title", marker)
        if tool_title is not marker and tool.title != tool_title:
            tool.title = tool_title
            tool_changed = True

        tool_obsolete = data.get("tool_obsolete", marker)
        if tool_obsolete is not marker and tool.obsolete != tool_obsolete:
            tool.obsolete = tool_obsolete
            tool_changed = True

        # If the tool has changed, we need to reindex it
        if tool_changed:
            tool.reindexObject()

        # Call the super method to apply changes to the survey
        return super().applyChanges(data)


class SurveyGroupQuaiveEditForm(QuaiveEditFormMixin, DefaultEditForm):
    """Custom edit form designed to be embedded in Quaive"""
