*** Setting ***
Library           Selenium2Library    10 seconds
Resource          secrets.robot
Library           DebugLibrary

*** Variable ***
#${SERVER}         ubuntung:4080/Plone2/client
${SERVER}         client.oiraproject.eu
${BROWSER}        firefox
${PROTOCOL}       http
${INVALID_USER_NAME}    null_user@syslab.com
${INVALID_USER_PASS}    nullpassword
${DEMO_SESSION_TOOLID}    demo/demo-garage-holder
${DEMO_SESSION_NAME}    robot_test_session
