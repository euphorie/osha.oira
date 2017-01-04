*** Setting ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  resource/common.robot
Resource  resource/keywords.robot

Test Setup        Prepare test browser
Test Teardown     Close all browsers

*** Test Case ***
User can register and delete account
    [Documentation]    Register a new user and delete the account again
    Go To    ${PROTOCOL}://${SERVER}/eu?set_language=en
    Click link "register"
    Register form should open
    Fill out and send register form
    Terms of conditions should open
    Accept terms of conditions
    User should be created
    Click link "delete account"
    Confirm delete account action
    Account should be deleted


User can change password
    [Documentation]    Change Password of existing user
    Given I am logged in as a user in OiRA EU
    Open account settings
    Change Password    ${USER_PASS}    ${USER_PASS_NEW}
    Then I log out
    Verify new Password
    Reset Password    ${USER_PASS_NEW}    ${USER_PASS}
