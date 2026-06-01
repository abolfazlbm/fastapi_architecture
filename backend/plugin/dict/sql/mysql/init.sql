set @system_menu_id = (select id from sys_menu where name = 'System');

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values ('dict.menu', 'PluginDict', '/plugins/dict', 8, 'fluent-mdl2:dictionary', 1, '/plugins/dict/views/index', null, 1, 1, 1, '', null, @system_menu_id, now(), null);

set @dict_menu_id = LAST_INSERT_ID();

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增类型', 'AddDictType', null, 0, null, 2, null, 'dict:type:add', 1, 0, 1, '', null, @dict_menu_id, now(), null),
('修改类型', 'EditDictType', null, 0, null, 2, null, 'dict:type:edit', 1, 0, 1, '', null, @dict_menu_id, now(), null),
('删除类型', 'DeleteDictType', null, 0, null, 2, null, 'dict:type:del', 1, 0, 1, '', null, @dict_menu_id, now(), null),
('新增数据', 'AddDictData', null, 0, null, 2, null, 'dict:data:add', 1, 0, 1, '', null, @dict_menu_id, now(), null),
('修改数据', 'EditDictData', null, 0, null, 2, null, 'dict:data:edit', 1, 0, 1, '', null, @dict_menu_id, now(), null),
('删除数据', 'DeleteDictData', null, 0, null, 2, null, 'dict:data:del', 1, 0, 1, '', null, @dict_menu_id, now(), null);

insert into sys_dict_type (id, name, code, remark, created_time, updated_time)
values
(1, 'General status', 'sys_status', 'System general status: 1/0', now(), null),
(2, 'Universal switch', 'sys_choose', 'System universal switch: true/false', now(), null),
(3, 'Menu type', 'sys_menu_type', 'System menu type', now(), null),
(4, 'Login status', 'sys_login_status', 'User login status', now(), null),
(5, 'Data rule operator', 'sys_data_rule_operator', 'Data permission rule operator', now(), null),
(6, 'Data rule expression', 'sys_data_rule_expression', 'Data permission rule expression', now(), null),
(7, 'Front-end parameter configuration', 'sys_frontend_config', 'Front-end parameter configuration type', now(), null),
(8, 'Task strategy type', 'task_strategy_type', 'Timed task strategy type', now(), null),
(9, 'task period type', 'task_period_type', 'scheduled task period type', now(), null),
(10, 'Notice', 'notice', 'Notification type', now(), null),
(11, 'Online status', 'user_online_status', 'User online status', now(), null),
(12, 'Plug-in type', 'sys_plugin_type', 'Plug-in type', now(), null);

insert into sys_dict_data (id, type_code, label, value, color, sort, status, remark, type_id, created_time, updated_time)
values
(1, 'sys_status', 'disabled', '0', 'red', 1, 1, 'disabled status', 1, now(), null),
(2, 'sys_status', 'normal', '1', 'green', 2, 1, 'normal status', 1, now(), null),
(3, 'sys_choose', 'closed', 'false', 'error', 1, 1, 'closed status', 2, now(), null),
(4, 'sys_choose', 'on', 'true', 'success', 2, 1, 'on state', 2, now(), null),
(5, 'sys_menu_type', 'directory', '0', 'orange', 1, 1, 'menu directory', 3, now(), null),
(6, 'sys_menu_type', 'menu', '1', 'default', 2, 1, 'normal menu', 3, now(), null),
(7, 'sys_menu_type', 'button', '2', 'processing', 3, 1, 'menu button', 3, now(), null),
(8, 'sys_menu_type', 'embedded', '3', 'cyan', 4, 1, 'embedded page', 3, now(), null),
(9, 'sys_menu_type', 'External link', '4', 'purple', 5, 1, 'External link', 3, now(), null),
(10, 'sys_login_status', 'Failed', '0', 'error', 1, 1, 'Login failed status', 4, now(), null),
(11, 'sys_login_status', 'success', '1', 'success', 2, 1, 'login successful status', 4, now(), null),
(12, 'sys_data_rule_operator', 'AND', '0', 'green', 1, 1, 'logical AND operator', 5, now(), null),
(13, 'sys_data_rule_operator', 'OR', '1', 'gold', 2, 1, 'logical OR operator', 5, now(), null),
(14, 'sys_data_rule_expression', 'Equal to (==)', '0', 'success', 1, 1, 'Equal to comparison expression', 6, now(), null),
(15, 'sys_data_rule_expression', 'Not equal to (!=)', '1', 'error', 2, 1, 'Not equal to comparison expression', 6, now(), null),
(16, 'sys_data_rule_expression', 'greater than (>)', '2', 'magenta', 3, 1, 'greater than comparison expression', 6, now(), null),
(17, 'sys_data_rule_expression', 'Greater than or equal to (>=)', '3', 'volcano', 4, 1, 'Greater than or equal to comparison expression', 6, now(), null),
(18, 'sys_data_rule_expression', 'less than (<)', '4', 'gold', 5, 1, 'less than comparison expression', 6, now(), null),
(19, 'sys_data_rule_expression', 'Less than or equal to (<=)', '5', 'orange', 6, 1, 'Less than or equal to comparison expression', 6, now(), null),
(20, 'sys_data_rule_expression', 'Include(in)', '6', 'purple', 7, 1, 'Include expression', 6, now(), null),
(21, 'sys_data_rule_expression', 'not in', '7', 'error', 8, 1, 'not in expression', 6, now(), null),
(22, 'sys_frontend_config', 'No', '0', 'red', 1, 1, 'Not a front-end parameter configuration', 7, now(), null),
(23, 'sys_frontend_config', 'is', '1', 'green', 2, 1, 'is the front-end parameter configuration', 7, now(), null),
(24, 'task_strategy_type', 'Interval', '0', 'cyan', 1, 1, 'time interval strategy', 8, now(), null),
(25, 'task_strategy_type', 'Crontab (Plan)', '1', 'purple', 2, 1, 'Time expression strategy', 8, now(), null),
(26, 'task_period_type', 'days', 'days', 'processing', 1, 1, 'Scheduled task cycle type-days', 9, now(), null),
(27, 'task_period_type', 'hours', 'hours', 'magenta', 2, 1, 'Scheduled task cycle type-hours', 9, now(), null),
(28, 'task_period_type', 'minutes', 'minutes', 'volcano', 3, 1, 'Scheduled task cycle type-minutes', 9, now(), null),
(29, 'task_period_type', 'seconds', 'seconds', 'gold', 4, 1, 'Scheduled task cycle type-seconds', 9, now(), null),
(30, 'task_period_type', 'microseconds', 'warning', 5, 1, 'Timing task cycle type-micro', 9, now(), null),
(31, 'notice', 'notification', '0', 'magenta', 1, 1, 'notification type', 10, now(), null),
(32, 'notice', 'announcement', '1', 'purple', 2, 1, 'notice type', 10, now(), null),
(33, 'user_online_status', 'offline', '0', 'warning', 1, 1, 'user offline status', 11, now(), null),
(34, 'user_online_status', 'online', '1', 'success', 2, 1, 'user online status', 11, now(), null),
(35, 'sys_plugin_type', 'Compressed package', '0', 'gold', 1, 1, 'Plugin type-compressed package', 12, now(), null),
(36, 'sys_plugin_type', 'GIT', '1', 'processing', 2, 1, 'plugin type-GIT', 12, now(), null);