*** Setting ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  resource/common.robot
Resource  resource/keywords.robot

Test Setup        Prepare test browser
Test Teardown     Close all browsers

*** Variable ***

${LOCATION1}    Fleet Street
${LOCATION2}    Sunrise Avenue

*** Test Case ***

Leather and Tanning Session
    Given I am logged in as a user in OiRA EU
     Then I start a new session  Leather & Tanning  Leather & Tanning Session
      And I traverse to the identification phase
     When I navigate to risk    1.1
     Then I can answer the risk as Yes   1.1
     When I navigate to risk    1.2
     Then I can answer the risk as No    1.2
     When I navigate to risk    1.4
      And I can supply the information for directly estimating the risk   1.4  medium
     Then I can add a custom risk  Beware of the cat  medium
     Then I can start an action plan module
     Then I fill in a measure description  Assess the team members and assign someone
     Then I fill in a prevention plan  Assess each person
     Then I fill in the requirements  Three years experience
     Then I fill in the responsible person  Jon Snow
     Then I save and continue
     Then I can fill in the custom risk  By being very quiet
     Then I can prepare a report
     Then I save and continue
     Then I give some feedback
     Then I save and continue
     Then I can download the action plan
     When I open the sessions dropdown
     Then I can delete the session    Leather & Tanning Session

Private Security Session
    Given I am logged in as a user in OiRA EU
     Then I start a new session  Private Security EU    Private Security multiple locations
      And I traverse to the profile screen
     Then I can enter two locations    Commercial manned guarding  ${LOCATION1}  ${LOCATION2}
     When I traverse to the module    Commercial manned guarding
     Then The locations are visible in the navigation    ${LOCATION1}  ${LOCATION2}
     When I navigate to submodule    2.2.3
     When I navigate to risk    2.2.3.1
     Then I can answer the risk as No    2.2.3.1
     When I navigate to risk    2.2.3.2
     Then I can answer the risk as No    2.2.3.2
     Then I can start a multi-location action plan module
     Then I fill in a measure description  Assess the team members and assign someone
     Then I fill in a prevention plan  Assess each person
     Then I fill in the requirements  Three years experience
     Then I fill in the responsible person  Cersei Lannister
     Then I add a custom Measure
     Then I use a Pre-fill for the Measure
     Then I save and continue
     Then I can remove an existing measure  Measure 2
     Then I can prepare a report
     Then I save and continue
     Then I give some feedback
     Then I save and continue
     Then I can download the action plan
     When I open the sessions dropdown
     Then I can delete the session    Private Security multiple locations

*** Keywords ***
I can fill in the custom risk
    [arguments]  ${description}
    Wait Until Page Contains Element  xpath=(//div[@class='topics']/ol/li[contains(@class, 'None')]/a)[last()]
    Click Element  xpath=(//div[@class='topics']/ol/li[contains(@class, 'None')]/a)[last()]
    Sleep  1
    Wait Until Element is visible  xpath=//textarea[@name="measure.action_plan:utf8:ustring:records"]
    Input Text  measure.action_plan:utf8:ustring:records  ${description}
    Click Button  Save and continue

I can add a custom risk
    [arguments]  ${description}  ${priority}
    Click Element  xpath=(//div[@class='topics']//a)[last()]
    Select Radio Button  skip_children:boolean  False
    Click Button  Next
    Wait until element is visible    id=description-1
    Input Text  risk.description:utf8:ustring:records  ${description}
    Select From List  risk.priority:utf8:ustring:records  ${priority}
    Click Button  Save and continue

I can supply the information to calculate the risk
    [arguments]  ${risk_number}  ${probability}  ${frequency}  ${effect}
    Element should not be visible     xpath=//fieldset[@id='evaluation']
    Click element    xpath=//fieldset[contains(@class, "pat-checklist radio")]/label[contains(text(), "No")]
    Wait until element is visible     xpath=//fieldset[@id='evaluation']
    Select Radio Button  probability:int  ${probability}
    Select Radio Button  frequency:int  ${frequency}
    Select Radio Button  effect:int  ${effect}
    Click button    Save and continue
    Wait until element is visible  xpath=//ol[@class='navigation questions']//li[@class='answered risk ' and contains(@title, '${risk_number}')]

I can supply the information for directly estimating the risk
    [arguments]  ${risk_number}  ${priority}
    Element should not be visible     xpath=//fieldset[@id='evaluation']
    Click element    xpath=//fieldset[contains(@class, "pat-checklist radio")]/label[contains(text(), "No")]
    Sleep  1
    Wait until element is visible     xpath=//fieldset[@id='evaluation']
    Select Radio Button  priority  ${priority}
    Click button    Save and continue
    Wait until element is visible  xpath=//ol[@class='navigation questions']//li[@class='answered risk ' and contains(@title, '${risk_number}')]

I can remove an existing measure
    [arguments]  ${measure_name}
    Click Button  Previous
    Wait until page contains element  xpath=//h2[.='${measure_name}']/following-sibling::*//a[contains(@class, 'icon-trash')]
    Click Link  xpath=//h2[.='${measure_name}']/following-sibling::*//a[contains(@class, 'icon-trash')]

I add a custom Measure
    Click Button  Add another measure

I use a Pre-fill for the Measure
    Click Element  xpath=(//a[.='Pre-fill'])[2]
    Click Element  xpath=(//ol[@class='add-measure-menu']/li/a)[last()]

I can prepare a report
    Click Link  Report
    Wait until page contains element  xpath=//li[@id="step-5" and @class="active"]


I can download the action plan
    Wait Until Page Contains  Download the action plan

I give some feedback
    Select From List  form.widgets.country  Germany
    Select Radio Button  form.widgets.employees  1-9

I save and continue
    Click Button  Save and continue
    Sleep  1

I fill in a measure description
    [arguments]    ${description}
    Input Text  measure.action_plan:utf8:ustring:records  ${description}

I fill in a prevention plan
    [arguments]    ${prevention_plan}
    Input Text  measure.prevention_plan:utf8:ustring:records  ${prevention_plan}

I fill in the requirements
    [arguments]    ${requirements}
    Input Text  measure.requirements:utf8:ustring:records  ${requirements}

I fill in the responsible person
    [arguments]    ${responsible}
    Input Text  measure.responsible:utf8:ustring:records  ${responsible}

I continue
    Click Link  Save and continue

I can start an action plan module
    Click Link  Action Plan
    Wait Until Page Contains Element  link=Action Plan
    Sleep  1
    Click Link  Create action plan
    Wait Until Page Contains Element  link=Next
    Click Link  Next

I can start a multi-location action plan module
    I can start an action plan module
    Set Test Message  Note: duplicate text "The next screens ..."
    Wait Until Page Contains Element  xpath=//li[contains(@class, 'submodule')]/ol
    Click Link  Next

I can select an existing session
    [arguments]  ${session_name}
    Click Element  xpath=//button[text()='${session_name}']

I can enter two locations
    [arguments]    ${module}  ${location1}  ${location2}
    Element should not be visible  xpath=//form//h2[contains(text(), "${module}")]/../fieldset[contains(@class, 'pat-checklist radio pat-depends')]
    Click element  xpath=//form//h2[contains(text(), "${module}")]/../fieldset[contains(@class, 'pat-checklist radio')]/label[contains(text(), 'Yes')]
    Element should be visible  xpath=//form//h2[contains(text(), "${module}")]/../fieldset[contains(@class, 'pat-checklist radio pat-depends')]
    Click element  xpath=//form//h2[contains(text(), "${module}")]/../fieldset[contains(@class, 'pat-checklist radio pat-depends')]/label[contains(text(), 'Yes')]
    Input text  xpath=//form//h2[contains(text(), "${module}")]/../fieldset[contains(@class, 'group')]/fieldset[contains(@class, 'pat-clone')]/label[@class='clone']/input  ${location1}
    Click button    Add another item
    Input text   xpath=//form//h2[contains(text(), "${module}")]/../fieldset[contains(@class, 'group')]/fieldset[contains(@class, 'pat-clone')]/label[@class='clone']/following-sibling::label/input  ${location2}
    Click button    Save and continue
    Wait until page contains element    xpath=//li[@id="step-2" and @class="active"]

I traverse to the module
    [arguments]     ${module}
    Sleep  1
    Click element  partial link=${module}
    Wait until page contains element    xpath=//h1[contains(text(), "${module}")]

The locations are visible in the navigation
    [arguments]    ${location1}  ${location2}
    Element should be visible  xpath=//h4[@class="location-tag" and .="${location1}"]
    Element should be visible  xpath=//h4[@class="location-tag" and .="${location2}"]

I traverse to the identification phase
    Click button    Start
    Wait until page contains element     xpath=//ol[@id="steps"]/li[@id="step-2" and @class="active"]
    Sleep  1

I traverse to the profile screen
    Click button    Start
    Wait until page contains    Tailor the risk assessment to your organisation

I navigate to risk
    [arguments]  ${risk_number}
    Click element  xpath=//ol[@class='navigation questions']//a/strong[.='${risk_number}']
    Wait until element is visible   xpath=//fieldset[@id="${risk_number}"]  2

I navigate to submodule
    [arguments]  ${risk_number}
    Click element  xpath=//li[contains(@class, 'submodule')]/a/strong[.='${risk_number}']

I can answer the risk as Yes
    [arguments]   ${risk_number}
    Wait until element is visible    xpath=//fieldset[contains(@class, "pat-checklist radio")]/label[contains(text(), "Yes")]
    Click element    xpath=//fieldset[contains(@class, "pat-checklist radio")]/label[contains(text(), "Yes")]
    Click button    Save and continue
    Wait until element is visible  xpath=//ol[@class='navigation questions']//li[@class='answered ' and contains(@title, '${risk_number}')]

I can answer the risk as No
    [arguments]   ${risk_number}
    Sleep  1
    Wait until page contains element    xpath=//fieldset[@id="${risk_number}"]/../fieldset[@id='evaluation']
    Element should not be visible     xpath=//fieldset[@id='evaluation']
    Click element    xpath=//fieldset[contains(@class, "pat-checklist radio")]/label[contains(text(), "No")]
    Wait until element is visible     xpath=//fieldset[@id='evaluation']
    Click button    Save and continue
    Wait until element is visible  xpath=//ol[@class='navigation questions']//li[@class='answered risk ' and contains(@title, '${risk_number}')]
