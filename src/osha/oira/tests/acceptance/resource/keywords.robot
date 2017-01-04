*** Keyword ***
Prepare test browser
    Open test browser
    Set window size  1300  900

Open OiRA
    Open Browser    http://${SERVER}    ${BROWSER}
    #Set Selenium Speed    3 second

Open OiRA EU
    #Set Selenium Speed    .3 seconds
    Go To    http://${SERVER}/eu/

I am logged in as a user in OiRA EU
    Open OiRA EU
    Log in as user
    Wait until element is visible  css=a#button-new-session
    Sleep  1


I am logged in as a user in OiRA EU again
    Open OiRA EU
    Log in as user again
    Wait until element is visible  css=a#button-new-session
    Sleep  1

Open OiRA EU and log in
    Open OiRA EU
    Log in as user

Try log in as user
    [Arguments]    ${arg1}=${USER_NAME}    ${arg2}=${USER_PASS}
    Wait until page contains    Login
    Click Link    Login
    Wait until page contains    Email address
    Input Text    __ac_name    ${arg1}
    Input Text    __ac_password:utf8:ustring    ${arg2}
    Click Button    Login

Log in as user
    [Arguments]    ${arg1}=${USER_NAME}    ${arg2}=${USER_PASS}
    Try log in as user    ${arg1}    ${arg2}
    # Note: if the "Splash message" gets removed, the following line must go too
    # Wait until element is visible  css=hr.trigger.pat-switch  2
    # Click element  css=hr.trigger.pat-switch
    Wait until page contains element   css=a.user-status

Log in as user again
    [Arguments]    ${arg1}=${USER_NAME}    ${arg2}=${USER_PASS}
    Try log in as user    ${arg1}    ${arg2}
    Wait until page contains element   css=a.user-status

I log out
    [Arguments]    ${loginname}=${USER_NAME}
    Sleep    1
    Click link    ${loginname}
    Wait until element is visible  xpath=//a[contains(@class, "user-status") and contains(@class, 'active')]
    Wait until element is visible    css=a.icon-logout
    Click link    Logout
    Wait until page contains    Welcome

Submit Form
    Wait Until Page Contains Element    css=button[type=submit]
    Click Button    css=button[type=submit]

Click link "register"
    Click Link    register

Register form should open
    Wait Until Page Contains Element    name=email
    Location Should Contain             /eu/register


Fill out and send register form
    Input Text    email    ${USER2_NAME}
    Input Text    password1:utf8:ustring    ${USER2_PASS}
    Input Text    password2:utf8:ustring    ${USER2_PASS}
    Click Button    xpath=//p[@class='buttonBar']/button[@value='next']
    Wait Until Page Contains Element    id=conditions

Terms of conditions should open
    Execute Javascript    window.document.getElementById('conditions').scrollTop=document.getElementById('conditions').scrollHeight;
    Element Should Be Enabled    id=agree-button

Accept terms of conditions
    Sleep  1
    Click Button    id=agree-button
    # Note: if the "Splash message" gets removed, the following line must go too
    # Wait until element is visible  css=hr.trigger.pat-switch  2
    # Click element  css=hr.trigger.pat-switch
    Wait until page contains    start a new session
    Wait until page contains element   css=a.user-status

Open account settings
    Sleep  1
    Click Link  css=a.user-status
    Wait until element is visible  xpath=//a[contains(@class, "user-status") and contains(@class, 'active')]
    Wait Until Page Contains    Delete account

Click link "delete account"
    Click Link    Delete account
    Wait Until Page Contains Element    xpath=//h1[text()='Delete account']

Confirm delete account action
    Input Text    form.widgets.password    ${USER2_PASS}
    Click Button    Delete account
    Wait Until Page Contains    Welcome

Account should be deleted
    Open OiRA EU
    Try log in as user    ${USER2_NAME}    ${USER2_PASS}
    Wait Until Page Contains    Your login name and/or password were entered incorrectly.

User should be created
    Open account settings

Change Password
    [Arguments]    ${arg1}    ${arg2}
    Click Link  Change password
    Input Text    form.widgets.old_password    ${arg1}
    Input Text    form.widgets.new_password    ${arg2}
    Input Text    form.widgets.new_password.confirm    ${arg2}
    Click Button    Save changes
    Wait Until Page Contains    Your password was successfully changed.
    Click Button   Close

Verify new Password
    Sleep  1
    Log in as user again   ${USER_NAME}    ${USER_PASS_NEW}

Reset Password
    [Arguments]    ${arg1}    ${arg2}
    Open account settings
    Change Password    ${arg1}    ${arg2}

I start a new session
    [arguments]    ${tool}   ${name}=My tool session name
    Click link    start a new session
    Wait until element is visible  css=select.oira_sessions_select
    Select From List By Label    css=select.oira_sessions_select   ${tool}
    Input text    title:utf8:ustring    ${name}
    Click button    Start session
    Wait until page contains    ${tool}

I open the sessions dropdown
    Element should be visible    id=button-sessions
    Sleep  1
    Click link  xpath=//a[@id='button-sessions']

I can delete the session
    [arguments]    ${session_name}
    Wait until element is visible    xpath=//button[contains(text(), '${session_name}')]/../../following-sibling::td[contains(@class, 'actions')]/a[contains(@class, 'icon-trash')]
    Click element    xpath=//button[contains(text(), '${session_name}')]/../../following-sibling::td[contains(@class, 'actions')]/a[contains(@class, 'icon-trash')]
    Wait until element is visible    xpath=//form[contains(@action, "delete-session")]/div/button[@type="submit"]
    Click button    Yes, delete session
    Wait Until Page Contains    Session `${session_name}` has been deleted.
