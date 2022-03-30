# Dont import this file, it's just for our i18n toolchain

from euphorie.content import MessageFactory as _


# euphorie/client/templates/account-settings.pt
_("header_account_data", default="Account data")
_("Email address/account name")
_("Change email address")
_("Delete Account")
_(
    "Please bear in mind that by changing the email address, your login name will also change."  # noqa: E501
)
_("header_password", default="Password")


# Copied from euphorie/client/templates/risk_actionplan.pt
# Currently, those modal dialogs are not implemented in oiranew
_(
    "Are you sure you want to delete this measure? This action can not be reverted.",
    default="Are you sure you want to delete this measure? This action can not be reverted.",  # noqa: E501
)
_(
    "The current text in the fields 'Action plan', 'Prevention plan' and 'Requirements' of this measure will be overwritten. This action cannot be reverted. Are you sure you want to continue?",  # noqa: E501
    default="The current text in the fields 'Action plan', 'Prevention plan' and 'Requirements' of this measure will be overwritten. This action cannot be reverted. Are you sure you want to continue?",  # noqa: E501
)
_("Standard solutions")

# More copied translations from euphorie
_(
    "help_evaluation_optional",
    default="This option allows users to skip the evaluation phase.",
)
_("label_evaluation_phase", default="Evaluation phase")
_("Description", default="Description")
_("evalmethod_fixed", default="Skip evaluation")
_("label_fixed_priority", default="priority")
# _(u"message_lock_warn", default=u"Please be aware that you have %s more login attempts before your account will be locked.")  # noqa: E501

_(
    "info_select_session",
    default="Select an earlier session to complete or review or ${start_session}.",
)

# Validation error messages
_("error_validation_date", default="This value must be a valid date.")
_("error_validation_email", default="This value must be a valid email address.")
_("error_validation_number", default="This value must be a number.")
_("error_validation_required", default="This value is required.")
