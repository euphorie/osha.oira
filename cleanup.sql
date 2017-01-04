DELETE FROM session WHERE account_id = (
    SELECT id FROM account WHERE loginname = 'jenkins_user@syslab.com'
);
DELETE FROM account WHERE loginname = 'jenkins_user2@syslab.com';