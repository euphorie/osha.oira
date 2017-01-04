*** Setting ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  resource/common.robot
Resource  resource/keywords.robot

Test Setup        Prepare test browser
Test Teardown     Close all browsers

*** Test Case ***
User can start a new session
    Given I am logged in as a user in OiRA EU
     When I start a new session  Leather & Tanning
     Then I land on the preparation screen

User can resume a session
    Given I am logged in as a user in OiRA EU
     Then I start a new session  Leather & Tanning    My test session for resuming
      And I log out
     When I am logged in as a user in OiRA EU again
     Then I can select the existing session    My test session for resuming

User can rename a session
    Given I am logged in as a user in OiRA EU
     Then I start a new session  Leather & Tanning    My test session for renaming
     When I open the sessions dropdown
     Then I can rename the session    My test session for renaming    My renamed session

User can delete a session
    Given I am logged in as a user in OiRA EU
     Then I start a new session  Leather & Tanning    My test session for deleting
     When I open the sessions dropdown
     Then I can delete the session    My test session for deleting


*** Keywords ***
I land on the preparation screen
    Element should be visible     xpath=//ol[@id="steps"]/li[@id="step-1" and @class="active"]

I can select the existing session
    [arguments]    ${name}
    Wait until page contains    ${name}

I can rename the session
    [arguments]    ${old_name}  ${new_name}
    Wait until element is visible    xpath=//button[contains(text(), '${old_name}')]/../../following-sibling::td[contains(@class, 'actions')]/a[contains(@class, 'icon-pencil')]
    Click link  xpath=//button[contains(text(), '${old_name}')]/../../following-sibling::td[contains(@class, 'actions')]/a[contains(@class, 'icon-pencil')]
    Wait until element is visible    xpath=//form[contains(@action, "rename-session")]
    Element should be visible    xpath=//input[@value="${old_name}"]
    Input text    form.widgets.title    ${new_name}
    Click button    Save changes
    Wait Until Page Contains    Session title has been changed to ${new_name}