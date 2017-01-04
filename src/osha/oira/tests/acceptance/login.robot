*** Setting ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  resource/common.robot
Resource  resource/keywords.robot

Test Setup        Prepare test browser
Test Teardown     Close all browsers

*** Test Case ***
Log in with valid credentials
    Open OiRA EU
    Log in as user
    Wait Until Page Contains    Select an earlier session to complete or review

Log in fail with invalid credentials
    Open OiRA EU
    Try log in as user  dummy@example.com  very-secret
    Wait Until Page Contains    Your login name and/or password were entered incorrectly.
