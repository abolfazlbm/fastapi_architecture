insert into sys_dept (id, name, sort, leader, phone, email, status, del_flag, parent_id, created_time, updated_time)
values (1, 'Test', 0, null, null, null, 1, 0, null, now(), null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(1, 'page.dashboard.title', 'Dashboard', '/dashboard', 0, 'ant-design:dashboard-outlined', 0, null, null, 1, 1, 1, '', null, null, '2025-06-26 20:29:06', null),
(2, 'page.dashboard.analytics', 'Analytics', '/analytics', 0, 'lucide:area-chart', 1, '/dashboard/analytics/index', null, 1, 1, 1, '', null, 1, '2025-06-26 20:29:06', null),
(3, 'page.dashboard.workspace', 'Workspace', '/workspace', 1, 'carbon:workspace', 1, '/dashboard/workspace/index', null, 1, 1, 1, '', null, 1, '2025-06-26 20:29:06', null),
(4, 'page.menu.system', 'System', '/system', 1, 'eos-icons:admin', 0, null, null, 1, 1, 1, '', null, null, '2025-06-26 20:29:06', null),
(5, 'page.menu.sysDept', 'SysDept', '/system/dept', 1, 'mingcute:department-line', 1, '/system/dept/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', null),
(6, 'Add', 'AddSysDept', null, 0, null, 2, null, 'sys:dept:add', 1, 0, 1, '', null, 5, '2025-06-26 20:29:06', null),
(7, 'Edit', 'EditSysDept', null, 0, null, 2, null, 'sys:dept:edit', 1, 0, 1, '', null, 5, '2025-06-26 20:29:06', null),
(8, 'Delete', 'DeleteSysDept', null, 0, null, 2, null, 'sys:dept:del', 1, 0, 1, '', null, 5, '2025-06-26 20:29:06', null),
(9, 'page.menu.sysUser', 'SysUser', '/system/user', 2, 'ant-design:user-outlined', 1, '/system/user/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', null),
(10, 'Delete', 'DeleteSysUser', null, 0, null, 2, null, 'sys:user:del', 1, 0, 1, '', null, 9, '2025-06-26 20:29:06', null),
(11, 'page.menu.sysRole', 'SysRole', '/system/role', 3, 'carbon:user-role', 1, '/system/role/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', null),
(12, 'Add', 'AddSysRole', null, 0, null, 2, null, 'sys:role:add', 1, 0, 1, '', null, 11, '2025-06-26 20:29:06', null),
(13, 'Edit', 'EditSysRole', null, 0, null, 2, null, 'sys:role:edit', 1, 0, 1, '', null, 11, '2025-06-26 20:29:06', null),
(14, 'Edit Role Menu', 'EditSysRoleMenu', null, 0, null, 2, null, 'sys:role:menu:edit', 1, 0, 1, '', null, 11, '2025-06-26 20:29:06', null),
(15, 'Edit Role Data Scope', 'EditSysRoleScope', null, 0, null, 2, null, 'sys:role:scope:edit', 1, 0, 1, '', null, 11, '2025-06-26 20:29:06', null),
(16, 'Delete', 'DeleteSysRole', null, 0, null, 2, null, 'sys:role:del', 1, 0, 1, '', null, 11, '2025-06-26 20:29:06', null),
(17, 'page.menu.sysMenu', 'SysMenu', '/system/menu', 4, 'ant-design:menu-outlined', 1, '/system/menu/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', null),
(18, 'Add', 'AddSysMenu', null, 0, null, 2, null, 'sys:menu:add', 1, 0, 1, '', null, 17, '2025-06-26 20:29:06', null),
(19, 'Edit', 'EditSysMenu', null, 0, null, 2, null, 'sys:menu:edit', 1, 0, 1, '', null, 17, '2025-06-26 20:29:06', null),
(20, 'Delete', 'DeleteSysMenu', null, 0, null, 2, null, 'sys:menu:del', 1, 0, 1, '', null, 17, '2025-06-26 20:29:06', null),
(21, 'page.menu.sysDataPermission', 'SysDataPermission', '/system/data-permission', 5, 'icon-park-outline:permissions', 0, null, null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', null),
(22, 'page.menu.sysDataScope', 'SysDataScope', '/system/data-scope', 6, 'cuida:scope-outline', 1, '/system/data-permission/scope/index', null, 1, 1, 1, '', null, 21, '2025-06-26 20:29:06', '2025-06-26 20:37:26'),
(23, 'Add', 'AddSysDataScope', null, 0, null, 2, null, 'data:scope:add', 1, 0, 1, '', null, 22, '2025-06-26 20:29:06', null),
(24, 'Edit', 'EditSysDataScope', null, 0, null, 2, null, 'data:scope:edit', 1, 0, 1, '', null, 22, '2025-06-26 20:29:06', null),
(25, 'Edit Data Scope Rule', 'EditDataScopeRule', null, 0, null, 2, null, 'data:scope:rule:edit', 1, 0, 1, '', null, 22, '2025-06-26 20:29:06', null),
(26, 'Delete', 'DeleteSysDataScope', null, 0, null, 2, null, 'data:scope:del', 1, 0, 1, '', null, 22, '2025-06-26 20:29:06', null),
(27, 'page.menu.sysDataRule', 'SysDataRule', '/system/data-rule', 7, 'material-symbols:rule', 1, '/system/data-permission/rule/index', null, 1, 1, 1, '', null, 21, '2025-06-26 20:29:06', '2025-06-26 20:37:40'),
(28, 'Add', 'AddSysDataRule', null, 0, null, 2, null, 'data:rule:add', 1, 0, 1, '', null, 27, '2025-06-26 20:29:06', null),
(29, 'Edit', 'EditSysDataRule', null, 0, null, 2, null, 'data:rule:edit', 1, 0, 1, '', null, 27, '2025-06-26 20:29:06', null),
(30, 'Delete', 'DeleteSysDataRule', null, 0, null, 2, null, 'data:rule:del', 1, 0, 1, '', null, 27, '2025-06-26 20:29:06', null),
(31, 'page.menu.sysPlugin', 'SysPlugin', '/system/plugin', 8, 'clarity:plugin-line', 1, '/system/plugin/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', null),
(32, 'Install', 'InstallSysPlugin', null, 0, null, 2, null, 'sys:plugin:install', 1, 0, 1, '', null, 31, '2025-06-26 20:29:06', null),
(33, 'Uninstall', 'UninstallSysPlugin', null, 0, null, 2, null, 'sys:plugin:uninstall', 1, 0, 1, '', null, 31, '2025-06-26 20:29:06', null),
(34, 'Edit', 'EditSysPlugin', null, 0, null, 2, null, 'sys:plugin:edit', 1, 0, 1, '', null, 31, '2025-06-26 20:29:06', null),
(35, 'page.menu.scheduler', 'Scheduler', '/scheduler', 2, 'material-symbols:automation', 0, null, null, 1, 1, 1, '', null, null, '2025-06-26 20:29:06', null),
(36, 'page.menu.schedulerManage', 'SchedulerManage', '/scheduler/manage', 1, 'ix:scheduler', 1, '/scheduler/manage/index', null, 1, 1, 1, '', null, 35, '2025-06-26 20:29:06', null),
(37, 'page.menu.schedulerRecord', 'SchedulerRecord', '/scheduler/record', 2, 'ix:scheduler', 1, '/scheduler/record/index', null, 1, 1, 1, '', null, 35, '2025-06-26 20:29:06', null),
(38, 'page.menu.log', 'Log', '/log', 3, 'carbon:cloud-logging', 0, null, null, 1, 1, 1, '', null, null, '2025-06-26 20:29:06', null),
(39, 'page.menu.login', 'LoginLog', '/log/login', 1, 'mdi:login', 1, '/log/login/index', null, 1, 1, 1, '', null, 38, '2025-06-26 20:29:06', null),
(40, 'Delete', 'DeleteLoginLog', null, 0, null, 2, null, 'log:login:del', 1, 0, 1, '', null, 39, '2025-06-26 20:29:06', null),
(41, 'Clear', 'EmptyLoginLog', null, 0, null, 2, null, 'log:login:clear', 1, 0, 1, '', null, 39, '2025-06-26 20:29:06', null),
(42, 'page.menu.opera', 'OperaLog', '/log/opera', 2, 'carbon:operations-record', 1, '/log/opera/index', null, 1, 1, 1, '', null, 38, '2025-06-26 20:29:06', null),
(43, 'Delete', 'DeleteOperaLog', null, 0, null, 2, null, 'log:opera:del', 1, 0, 1, '', null, 42, '2025-06-26 20:29:06', null),
(44, 'Clear', 'EmptyOperaLog', null, 0, null, 2, null, 'log:opera:clear', 1, 0, 1, '', null, 42, '2025-06-26 20:29:06', null),
(45, 'page.menu.monitor', 'Monitor', '/monitor', 4, 'mdi:monitor-eye', 0, null, null, 1, 1, 1, '', null, null, '2025-06-26 20:29:06', null),
(46, 'page.menu.online', 'Online', '/log/online', 1, 'wpf:online', 1, '/monitor/online/index', null, 1, 1, 1, '', null, 45, '2025-06-26 20:29:06', null),
(47, 'Kick Out', 'KickOutOnline', null, 0, null, 2, null, 'sys:session:delete', 1, 0, 1, '', null, 46, '2025-06-26 20:29:06', null),
(48, 'page.menu.redis', 'Redis', '/monitor/redis', 2, 'devicon:redis', 1, '/monitor/redis/index', null, 1, 1, 1, '', null, 45, '2025-06-26 20:29:06', null),
(49, 'page.menu.server', 'Server', '/monitor/server', 3, 'mdi:server-outline', 1, '/monitor/server/index', null, 1, 1, 1, '', null, 45, '2025-06-26 20:29:06', null),
(50, 'Project', 'Project', '/fba', 5, 'https://wu-clan.github.io/picx-images-hosting/logo/fba.png', 0, null, null, 1, 1, 1, '', null, null, '2025-06-26 20:29:06', null),
(51, 'Document', 'Document', '/fba/document', 1, 'lucide:book-open-text', 4, '/_core/fallback/iframe.vue', null, 1, 1, 1, 'https://fastapi-practices.github.io/fastapi_best_architecture_docs', null, 50, '2025-06-26 20:29:06', null),
(52, 'Github', 'Github', '/fba/github', 2, 'ant-design:github-filled', 4, '/_core/fallback/iframe.vue', null, 1, 1, 1, 'https://github.com/fastapi-practices/fastapi_best_architecture', null, 50, '2025-06-26 20:29:06', null),
(53, 'Apifox', 'Apifox', '/fba/apifox', 3, 'simple-icons:apifox', 3, '/_core/fallback/iframe.vue', null, 1, 1, 1, 'https://apifox.com/apidoc/shared-28a93f02-730b-4f33-bb5e-4dad92058cc0', null, 50, '2025-06-26 20:29:06', null),
(54, 'page.menu.profile', 'Profile', '/profile', 6, 'ant-design:profile-outlined', 1, '/_core/profile/index', null, 1, 0, 1, '', null, null, '2025-06-26 20:29:06', null),
(55, 'config.menu', 'PluginConfig', '/plugins/config', 7, 'codicon:symbol-parameter', 1, '/plugins/config/views/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', '2025-06-26 20:34:51'),
(56, 'Add', 'AddConfig', null, 0, null, 2, null, 'sys:config:add', 1, 0, 1, '', null, 55, '2025-06-26 20:29:06', null),
(57, 'Edit', 'EditConfig', null, 0, null, 2, null, 'sys:config:edit', 1, 0, 1, '', null, 55, '2025-06-26 20:29:06', null),
(58, 'Delete', 'DeleteConfig', null, 0, null, 2, null, 'sys:config:del', 1, 0, 1, '', null, 55, '2025-06-26 20:29:06', null),
(59, 'dict.menu', 'PluginDict', '/plugins/dict', 8, 'fluent-mdl2:dictionary', 1, '/plugins/dict/views/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', '2025-06-26 20:35:07'),
(60, 'Add Dict Type', 'AddDictType', null, 0, null, 2, null, 'dict:type:add', 1, 0, 1, '', null, 59, '2025-06-26 20:29:06', null),
(61, 'Edit Dict Type', 'EditDictType', null, 0, null, 2, null, 'dict:type:edit', 1, 0, 1, '', null, 59, '2025-06-26 20:29:06', null),
(62, 'Delete Dict Type', 'DeleteDictType', null, 0, null, 2, null, 'dict:type:del', 1, 0, 1, '', null, 59, '2025-06-26 20:29:06', null),
(63, 'Add Dict Data', 'AddDictData', null, 0, null, 2, null, 'dict:data:add', 1, 0, 1, '', null, 59, '2025-06-26 20:29:06', null),
(64, 'Edit Dict Data', 'EditDictData', null, 0, null, 2, null, 'dict:data:edit', 1, 0, 1, '', null, 59, '2025-06-26 20:29:06', null),
(65, 'Delete Dict Data', 'DeleteDictData', null, 0, null, 2, null, 'dict:data:del', 1, 0, 1, '', null, 59, '2025-06-26 20:29:06', null),
(66, 'notice.menu', 'PluginNotice', '/plugins/notice', 9, 'fe:notice-push', 1, '/plugins/notice/views/index', null, 1, 1, 1, '', null, 4, '2025-06-26 20:29:06', '2025-06-26 20:35:14'),
(67, 'Add', 'AddNotice', null, 0, null, 2, null, 'sys:notice:add', 1, 0, 1, '', null, 66, '2025-06-26 20:29:06', null),
(68, 'Edit', 'EditNotice', null, 0, null, 2, null, 'sys:notice:edit', 1, 0, 1, '', null, 66, '2025-06-26 20:29:06', null),
(69, 'Delete', 'DeleteNotice', null, 0, null, 2, null, 'sys:notice:del', 1, 0, 1, '', null, 66, '2025-06-26 20:29:06', null),
(70, 'code_generator.menu', 'PluginCodeGenerator', '/plugins/code-generator', 10, 'tabler:code', 1, '/plugins/code_generator/views/index', null, 1, 1, 1, '', null, null, '2025-06-26 20:29:06', '2025-06-26 20:35:25'),
(71, 'Add Business', 'AddGenCodeBusiness', '', 0, null, 2, null, 'codegen:business:add', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', '2025-06-26 20:45:16'),
(72, 'Edit Business', 'EditGenCodeBusiness', null, 0, null, 2, null, 'codegen:business:edit', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', null),
(73, 'Delete Business', 'DeleteGenCodeBusiness', null, 0, null, 2, null, 'codegen:business:del', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', null),
(74, 'Add Model', 'AddGenCodeModel', null, 0, null, 2, null, 'codegen:model:add', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', null),
(75, 'Edit Model', 'EditGenCodeModel', null, 0, null, 2, null, 'codegen:model:edit', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', null),
(76, 'Delete Model', 'DeleteGenCodeModel', null, 0, null, 2, null, 'codegen:model:del', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', null),
(77, 'Import', 'ImportGenCode', null, 0, null, 2, null, 'codegen:table:import', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', null),
(78, 'Write', 'WriteGenCode', null, 0, null, 2, null, 'codegen:local:write', 1, 0, 1, '', null, 70, '2025-06-26 20:29:06', null);

insert into sys_role (id, name, status, is_filter_scopes, remark, created_time, updated_time)
values (1, 'Test', 1, 1, null, now(), null);

insert into sys_role_menu (id, role_id, menu_id)
values
(1, 1, 1),
(2, 1, 2),
(3, 1, 3),
(4, 1, 54);

insert into sys_user (id, uuid, username, nickname, password, salt, email, is_superuser, is_staff, status, is_multi_login, avatar, phone, join_time, last_login_time, dept_id, created_time, updated_time)
values
(1, uuid(), 'admin', 'User88888', '$2b$12$8y2eNucX19VjmZ3tYhBLcOsBwy9w1IjBQE4SSqwMDL5bGQVp2wqS.', unhex('24326224313224387932654E7563583139566A6D5A33745968424C634F'), 'admin@example.com', 1, 1, 1, 1, null, null, now(), now(), 1, now(), null),
(2, uuid(), 'test', 'User66666', '$2b$12$BMiXsNQAgTx7aNc7kVgnwedXGyUxPEHRnJMFbiikbqHgVoT3y14Za', unhex('24326224313224424D6958734E514167547837614E63376B56676E7765'), 'test@example.com', 0, 0, 1, 0, null, null, now(), now(), 1, now(), null);

insert into sys_user_role (id, user_id, role_id)
values
(1, 1, 1),
(2, 2, 1);

insert into sys_data_scope (id, name, status, created_time, updated_time)
values
(1, 'Test Department Data Permission', 1, now(), null),
(2, 'Test Department and Subordinate Data Permission', 1, now(), null);

insert into sys_data_rule (id, name, model, `column`, operator, expression, `value`, created_time, updated_time)
values
(1, 'Department Name Equals Test', 'Department', 'name', 1, 0, 'Test', now(), null),
(2, 'Parent Department ID Equals 1', 'Department', 'parent_id', 0, 0, '1', now(), null);

insert into sys_data_scope_rule (id, data_scope_id, data_rule_id)
values
(1, 1, 1),
(2, 2, 1),
(3, 2, 2);