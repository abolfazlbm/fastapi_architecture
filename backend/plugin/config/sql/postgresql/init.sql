insert into sys_config (id, name, type, "key", value, is_frontend, remark, created_time, updated_time)
values
(1, 'STATUS', 'EMAIL', 'EMAIL_CONFIG_STATUS', '1', false, null, now(), null),
(2, 'Server address', 'EMAIL', 'EMAIL_HOST', 'smtp.qq.com', false, null, now(), null),
(3, 'Server port', 'EMAIL', 'EMAIL_PORT', '465', false, null, now(), null),
(4, 'Email account', 'EMAIL', 'EMAIL_USERNAME', 'fba@qq.com', false, null, now(), null),
(5, 'Email password', 'EMAIL', 'EMAIL_PASSWORD', '', false, null, now(), null),
(6, 'SSL encryption', 'EMAIL', 'EMAIL_SSL', 'true', false, null, now(), null),
(7, 'STATUS', 'USER_SECURITY', 'USER_SECURITY_CONFIG_STATUS', '1', false, null, now(), null),
(8, 'Password error lock threshold', 'USER_SECURITY', 'USER_LOCK_THRESHOLD', '5', false, '0 means locking is disabled', now(), null),
(9, 'Password incorrect lock duration (seconds)', 'USER_SECURITY', 'USER_LOCK_SECONDS', '300', false, null, now(), null),
(10, 'Password validity period (days)', 'USER_SECURITY', 'USER_PASSWORD_EXPIRY_DAYS', '365', false, '0 means never expires', now(), null),
(11, 'Password expiry reminder (days)', 'USER_SECURITY', 'USER_PASSWORD_REMINDER_DAYS', '7', false, '0 means no reminder', now(), null),
(12, 'Number of password history checks', 'USER_SECURITY', 'USER_PASSWORD_HISTORY_CHECK_COUNT', '3', false, null, now(), null),
(13, 'Minimum password length', 'USER_SECURITY', 'USER_PASSWORD_MIN_LENGTH', '6', false, null, now(), null),
(14, 'Maximum password length', 'USER_SECURITY', 'USER_PASSWORD_MAX_LENGTH', '32', false, null, now(), null),
(15, 'Password must contain special characters', 'USER_SECURITY', 'USER_PASSWORD_REQUIRE_SPECIAL_CHAR', 'false', false, null, now(), null),
(16, 'STATUS', 'LOGIN', 'LOGIN_CONFIG_STATUS', '1', false, null, now(), null),
(17, 'Verification code switch', 'LOGIN', 'LOGIN_CAPTCHA_ENABLED', 'true', false, null, now(), null);
select setval(pg_get_serial_sequence('sys_config', 'id'),coalesce(max(id), 0) + 1, true) from sys_config;
