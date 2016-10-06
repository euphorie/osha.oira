# Dont import this file, it's just for our i18n toolchain

from euphorie.content import MessageFactory as _

# euphorie/client/templates/account-settings.pt
_("header_account_data", default=u"Account data")
_("Email address/account name")
_("Change email address")
_("Delete Account")
_("Please bear in mind that by changing the email address, your login name will also change.")
_("header_password", default=u"Password")


# Copied from euphorie/client/templates/risk_actionplan.pt
# Currently, those modal dialogs are not implemented in oiranew
_(u"Are you sure you want to delete this measure? This action can not be reverted.",
    default=u"Are you sure you want to delete this measure? This action can not be reverted.")
_(u"The current text in the fields 'Action plan', 'Prevention plan' and 'Requirements' of this measure will be overwritten. This action cannot be reverted. Are you sure you want to continue?",
    default=u"The current text in the fields 'Action plan', 'Prevention plan' and 'Requirements' of this measure will be overwritten. This action cannot be reverted. Are you sure you want to continue?")
_(u"Standard solutions")

# More copied translations from euphorie
_(u"help_evaluation_optional", default=u"This option allows users to skip the evaluation phase.")
_(u"label_evaluation_phase", default=u"Evaluation phase")
_(u"Description", default=u"Description")
_(u"evalmethod_fixed", default=u"Skip evaluation")
_(u"label_fixed_priority", default=u"priority")
# _(u"message_lock_warn", default=u"Please be aware that you have %s more login attempts before your account will be locked.")

# Validation error messages
_("error_validation_date", default=u"This value must be a valid date.")
_("error_validation_email", default=u"This value must be a valid email address.")
_("error_validation_number", default=u"This value must be a number.")
_("error_validation_required", default="This value is required.")
