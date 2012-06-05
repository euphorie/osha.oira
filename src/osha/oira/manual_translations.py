# Dont import this file, it's just for our i18n toolchain

from euphorie.content import MessageFactory as _

_("help_measure_action_plan", default=u"Describe your general approach to "
    u"eliminate or (if the risk is not avoidable) reduce the risk.")
_("help_measure_prevention_plan", default=u"Describe the specific action(s) "
    u"required to implement this approach (to eliminate or to reduce the "
    u"risk).")
_("help_measure_requirements", default=u'Describe: 1) what is your general '
    u"approach to eliminate or (if the risk is not avoidable) reduce the "
    u"risk; 2) the specific action(s) required to implement this approach "
    u"(to eliminate or to reduce the risk); 3) the level of expertise needed "
    u'to implement the measure, for instance "common sense (no OSH knowledge '
    u'required)", "no specific OSH expertise, but minimum OSH knowledge or '
    u'training and/or consultation of OSH guidance required", or "OSH '
    u'expert". You can also describe here any other additional requirement '
    u"(if any).")
_("Solution", default=u"Measure")
_("title_common_solution", default="Measure")
_("A solution.", default=u"A standard measure for a risk.")
_("header_solutions", default=u"Standard measures")

# euphorie/client/templates/account-settings.pt
_("header_account_data", default=u"Account data")
_("Email address/account name")
_("Change email address")
_("Delete Account")
_("Please bear in mind that by changing the email address, your login name will also change.")
_("header_password", default=u"Password")

_("risk_solution_header", default=u"Measure ${number}")
_("nav_surveys", default=u"OiRA Tools")
_("Survey", default=u"OiRA Tool")
_("help_header_sessions", default=u"Sessions")
_("label_sessions", default=u"Sessions")
_("Survey import", default=u"OiRA Tool import")
_("Import survey version", default=u"Import OiRA tool version")
_("Survey version", default=u"OiRA Tool version")
_("no_profile_questions", default=u"This OiRA Tool has no profile questions.")
_("button_create_new", default=u"Create new OiRA Tool")
_("message_choose_country", default=u"Please choose a country of which you "
    u"would like to view or copy an OiRA Tool.")
_("intro_select_sector", default="Select a sector for which you would like to "
    u"view or copy an OiRA Tool.")
_("help_survey_title", default=u"This is the title of this OiRA Tool "
    u"version. This name is never shown to users.")
_("help_introduction", default=u"The introduction text is shown when starting "
    u"a new OiRA Tool session. If no introduction is provided here a standard "
    u"text will be shown. Please keep this text brief so it will easily fit "
    u"on screens of small devices such as phones and PDAs.")
_("message_delete_no_last_survey", default=u"You cannot delete the only OiRA "
    u"Tool version.")
_("label_surveygroup_title", default=u"Title of imported OiRA Tool")
_("upload_success", default=u"Succesfully imported the OiRA Tool")
_("title_import_sector_survey", default=u"Import sector and OiRA Tool")
_("intro_add_survey", default=u"The form will allow you to create a new OiRA "
    u"Tool revision.")
_("help_risks_present", default=u"Now that you have identified the existing "
    u"hazards/problems in your company/organisation you need to evaluate the "
    u"risks arising from them.")
_("label_solution_direction", default=u"Solution")
_("Succesfully published the survey", default=u"Succesfully published the "
    u"OiRA Tool")
_("Succesfully created a preview for the survey. It can be accessed at "
    u"${url} .", default=u"Succesfully created a preview for the OiRA Tool. "
    u"It can be accessed at ${url}.")
_("help_publish", default=u"Publish the selected OiRA Tool live with its "
    u"latest changes.")
_("help_add_version", default=u"Create a duplicate of the selected OiRA Tool")
_("help_evaluation_optional", default=u"The option allows the end-user to "
    u"skip the Evaluation step.")
_("help_profilequestion_question", default=u'If this is to be "optional", '
    u'it must be formulated so that it is answerable with YES (the end-user '
    u'will have to tick a box) or NO (e.g. "Do you work with the public?"). '
    u'If this is to be "repeatable", it must be formulated as a prompt to '
    u'fill in multiple values (e.g. "List your different work locations").')
_("description_profilequestion", default=u"The basic architecture of an "
    u"Online interactive Risk Assessment consists of: - profile questions "
    u"(questions defining the company profile) - modules and sub-modules - "
    u"risks (affirmative statements). Profile questions are used to determine "
    u"whether particular modules apply to the end user at all (OPTIONAL), or "
    u"whether they should be repeated a number of times (REPEATABLE). Such "
    u"questions are asked BEFORE starting the risk identification and "
    u"evaluation. If the end-user does not confirm that an optional profile "
    u"question is relevant (by ticking the box), then the corresponding "
    u"module will be skipped entirely. If the end-user enters more than one "
    u"option to a repeatable profile question then the corresponding module "
    u"will be repeated the specified number of times.")
_("help_module_description", default=u"Include any relevant information that "
    u"may be helpful for the end-user.")
_("help_module_optional", default=u"Allows the end-user to skip this module "
    u"and everything inside it.")
_("help_module_question", default=u"The question to ask the end-user if this "
    u"module is optional. It must be formulated so that it is answerable with "
    u"YES (the end-user will have to tick a box) or NO")
_("help_solution_direction", default=u"This information will appear in the "
    u"Action plan step and should include an overview of general solution(s) "
    u"related to this module.")
_("label_statement", default=u"Affirmative statement")
_("label_problem_description", default=u"Negative statement")
_("help_statement", default=u"This is a short affirmative statement about a "
    u"possible risk (e.g. The building is well maintained.)")
_("help_problem_description", default=u"This is the inverse of the "
    u"affirmative statement (e.g. The building is not well maintained.)")
_("help_risk_description", default=u"Describe the risk. Include any relevant "
    u"information that may be helpful for the end-user.")
_("risktype_top5", default=u"Priority risk")
_("help_risk_type", default=u'"Priority risk" is one of the high risks in '
    u'the sector. "Risk" is related to the workplace or to the work carried '
    u'out. "Policy" refers to agreements, procedures, and management '
    u'decisions.')
_("help_default_priority", default=u"You can help the end-user by selecting a "
    u"default priority. He/she can still change the priority.")
_("help_default_severity", default=u"Indicate the severity if this risk "
    u"occurs.")
_("help_help_introduction", default=u"General information on risk assessment")
_("help_authentication", default=u"This text should explain how to register "
    u"and login.")
_("help_sessions", default=u"This text should describe the main functions of "
    u"the OiRA Tool.")
_("help_preparation", default=u"This text should explain the 2 types of "
    u"profile questions.")
_("help_identification", default=u"This text should explain how the risk "
    u"identification works.")
_("help_evaluation", default=u"This text should explain how to evaluate the "
    u"identified risks.")
_("help_actionplan", default=u"This text should explain how to fill in the "
    u"Action plan.")
_("help_reports", default=u"This text should describe how the report can "
    u"either be saved or printed.")
_("help_finalwords", default=u"General final recommendations.")

# 3044:
_("intro_print_identification_1", default=\
    u"It is possible for you to print out the contents of the tool to enable "
    u"you to look for the information at the relevant workplace (by walking "
    u"around and looking at what could cause harm, or by consulting the "
    u"workers and/or their representatives about problems they have "
    u"encountered). You can then introduce the information into the tool.")

_("intro_print_identification_2", default=\
    u"You may also wish to distribute the contents among the workers and/or "
    u"their representatives and invite them to participate in identifying the "
    u"hazards/problems, evaluating the risks and deciding on preventive action." 
    u"Their feedback should be taken into account when filling in this tool.")

_("list_of_risks", default=u"contents of the tool")

_("help_evaluation_empty", default=\
    u"No hazards or problems were spotted. Please proceed directly to the "
    u"action plan step.")

_("help_create_new_version", default=u"Start to write a new OiRA Tool. You "
    u"will be asked whether you want to start off with a copy of an existing "
    u"OiRA Tool..")

_("title_help_unpublished", default=u"Remove this OiRA Tool from the online "
    u"client.")

_("message_preview_success", default=u"Succesfully created a preview for the "
    u"OiRA Tool. It can be accessed at ${url} .")

_("warning_account_delete_surveys", default=u""
    u"Please note that by deleting your account, you will also delete all your "
    u"sessions. Please make sure you download your reports from the Report step prior "
    u"to deleting your account, if you want to keep any. ")

_("intro_preview", default=u""
    u"Are you sure you want to create a preview of this OiRA Tool? You can give the "
    u"URL for the preview to others so they can test the OiRA Tool. To access the "
    u"preview a standard OiRA client login is required.")

_("header_preview", default=u"Preview OiRA Tool")

_("help_publish_url", default=u"After publication the OiRA Tool will be available at ${url}.")

_("intro_publish_other_survey_published", default=u""
    u"Are you sure you want to publish this OiRA Tool version? This will replace the "
    u"current version.")

_("intro_publish_survey_published", default=u""
    u"Are you sure you want to republish this OiRA Tool? This will make all changes "
    u"made public.")

_("intro_publish_first_time", default=u""
    u"Are you sure you want to publish this OiRA Tool? After publication the OiRA Tool "
    u"will appear in the online client and be accessible by all users.")

_("header_publish", default="Publish OiRA Tool")

_("expl_update", default=u""
    u"This OiRA tool has changed since you last accessed it. Before you can "
    u"continue, you need to update to these changes.")

_("title_updated", default="OiRA Tool was updated")

_("help_surveygroup_title", default=u""
    u"The title of this OiRA Tool. This title is used in the OiRA Tool overview in the "
    u"clients.")

_("message_unpublish_success", default=u"This OiRA Tool is now no longer available in the client.")

_("label_upload_survey_title", default=u"Name for OiRA Tool version")

_("unpublish_confirm", default=u"Are you sure you want to unpublish this OiRA Tool?")

_("menu_import", default=u"Import OiRA Tool")

_("message_no_delete_published_survey", default=u"You cannot delete an OiRA Tool version that is published. Please unpublish it first.")

_("message_not_delete_published_sector", default=u"You can not delete a sector that contains published OiRA Tools."), 

_("add_survey", default="add a new OiRA Tool")

_("no_surveys_present", default="There are no OiRA Tools present. You can ${add_link}.")

_("header_sector_survey_list", default="OiRA Tools")

_("expl_error", default="We're sorry, but an unforseen error has occured.")



