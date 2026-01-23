insert into gen_business (id, app_name, table_name, doc_comment, table_comment, class_name, schema_name, filename, datetime_mixin, api_version, gen_path, remark, created_time, updated_time)
values (1, 'test', 'sys_opera_log', 'Operation log table', 'Operation log table', 'SysOperaLog', 'SysOperaLog', 'sys_opera_log', true, 'v1', null, null, '2025-12-15 15:30:33', null);

insert into gen_column (id, name, comment, type, pd_type, `default`, sort, `length`, is_pk, is_nullable, gen_business_id)
values
(1, 'trace_id', 'Request Trace ID', 'String', 'str', null, 2, 32, false, false, 1),
(2, 'username', 'username', 'String', 'str', null, 3, 64, false, true, 1),
(3, 'method', 'Request Type', 'String', 'str', null, 4, 32, false, false, 1),
(4, 'title', 'Operation module', 'String', 'str', null, 5, 256, false, false, 1),
(5, 'path', 'request path', 'String', 'str', null, 6, 512, false, false, 1),
(6, 'ip', 'IP address', 'String', 'str', null, 7, 64, false, false, 1),
(7, 'country', 'country', 'String', 'str', null, 8, 64, false, true, 1),
(8, 'region', 'region', 'String', 'str', null, 9, 64, false, true, 1),
(9, 'city', 'city', 'String', 'str', null, 10, 64, false, true, 1),
(10, 'user_agent', 'Request header', 'String', 'str', null, 11, 512, false, false, 1),
(11, 'os', 'operating system', 'String', 'str', null, 12, 64, false, true, 1),
(12, 'browser', 'browser', 'String', 'str', null, 13, 64, false, true, 1),
(13, 'device', 'device', 'String', 'str', null, 14, 64, false, true, 1),
(14, 'args', 'request parameters', 'JSON', 'dict', null, 15, 0, false, true, 1),
(15, 'status', 'Operation status (0 abnormal 1 normal)', 'INTEGER', 'int', null, 16, 0, false, false, 1),
(16, 'code', 'Operation status code', 'String', 'str', null, 17, 32, false, false, 1),
(17, 'msg', 'prompt message', 'TEXT', 'str', null, 18, 0, false, true, 1),
(18, 'cost_time', 'Request time (ms)', 'String', 'str', null, 19, 0, false, false, 1),
(19, 'opera_time', 'opera_time', 'String', 'str', null, 20, 0, false, false, 1);