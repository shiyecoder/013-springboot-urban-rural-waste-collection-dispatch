-- ============================================================
-- 城乡垃圾清运调度与台账管理系统  初始化脚本 (MySQL 8 / utf8mb4)
-- 库名 new_013。每张表均含测试数据，create_time 分布在近 6 个月。
-- 默认账号：admin / admin123（运营管理员），其余账号同密码
-- ============================================================
DROP DATABASE IF EXISTS new_013;
CREATE DATABASE new_013 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE new_013;


-- 组织机构 / 责任单位
CREATE TABLE sys_org (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  org_name VARCHAR(100) NOT NULL COMMENT '单位名称',
  org_type VARCHAR(20) NOT NULL COMMENT '类型：环卫所/物业/园区/乡镇',
  area VARCHAR(50) NOT NULL COMMENT '所属区域',
  leader VARCHAR(30) DEFAULT NULL COMMENT '负责人',
  phone VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  sort INT DEFAULT 0,
  status TINYINT DEFAULT 1 COMMENT '1 正常 0 停用',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0
) ENGINE=InnoDB COMMENT='责任单位';

-- 角色
CREATE TABLE sys_role (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_code VARCHAR(30) NOT NULL UNIQUE COMMENT '角色编码',
  role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
  data_scope VARCHAR(20) NOT NULL COMMENT '数据范围 SELF/DEPT/ORG/ALL',
  remark VARCHAR(200) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='角色';

-- 菜单
CREATE TABLE sys_menu (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  parent_id BIGINT DEFAULT 0,
  menu_name VARCHAR(60) NOT NULL,
  path VARCHAR(120) DEFAULT NULL COMMENT '前端路由',
  icon VARCHAR(40) DEFAULT NULL,
  menu_type CHAR(1) DEFAULT 'M' COMMENT 'M 菜单 B 按钮',
  perm VARCHAR(80) DEFAULT NULL COMMENT '权限标识',
  sort INT DEFAULT 0,
  visible TINYINT DEFAULT 1 COMMENT '1 显示 0 隐藏（菜单管理项自身隐藏）',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='菜单';

CREATE TABLE sys_role_menu (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_id BIGINT NOT NULL,
  menu_id BIGINT NOT NULL,
  UNIQUE KEY uk_role_menu (role_id, menu_id)
) ENGINE=InnoDB COMMENT='角色菜单';

-- 用户
CREATE TABLE sys_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL COMMENT 'BCrypt',
  real_name VARCHAR(30) NOT NULL,
  avatar VARCHAR(200) DEFAULT NULL COMMENT '头像相对路径',
  phone VARCHAR(20) DEFAULT NULL,
  email VARCHAR(80) DEFAULT NULL,
  org_id BIGINT DEFAULT NULL,
  role_id BIGINT NOT NULL,
  point_id BIGINT DEFAULT NULL COMMENT '收集点管理员绑定点位',
  driver_id BIGINT DEFAULT NULL COMMENT '司机账号绑定司机档案',
  status TINYINT DEFAULT 1,
  login_fail INT DEFAULT 0 COMMENT '连续登录失败次数',
  lock_until DATETIME DEFAULT NULL COMMENT '锁定截止时间',
  last_login DATETIME DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0
) ENGINE=InnoDB COMMENT='用户';

CREATE TABLE sys_dict (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  dict_type VARCHAR(50) NOT NULL,
  dict_label VARCHAR(60) NOT NULL,
  dict_value VARCHAR(40) NOT NULL,
  sort INT DEFAULT 0,
  status TINYINT DEFAULT 1
) ENGINE=InnoDB COMMENT='字典';

CREATE TABLE sys_message (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(120) NOT NULL,
  content VARCHAR(500) NOT NULL,
  biz_type VARCHAR(30) NOT NULL COMMENT '业务类型',
  biz_no VARCHAR(40) DEFAULT NULL COMMENT '业务编号，用于详情跳转',
  receiver_id BIGINT NOT NULL,
  read_flag TINYINT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='站内消息';

CREATE TABLE sys_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT DEFAULT NULL,
  user_name VARCHAR(30) DEFAULT NULL,
  module VARCHAR(50) DEFAULT NULL,
  action VARCHAR(50) DEFAULT NULL,
  method VARCHAR(160) DEFAULT NULL,
  params VARCHAR(500) DEFAULT NULL,
  ip VARCHAR(40) DEFAULT NULL,
  cost_ms INT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='操作日志';

-- 垃圾类型已并入字典；处置场
CREATE TABLE dispose_site (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  site_code VARCHAR(40) NOT NULL UNIQUE,
  site_name VARCHAR(80) NOT NULL,
  address VARCHAR(150) NOT NULL,
  capacity DECIMAL(10,2) NOT NULL COMMENT '日处理能力(吨)',
  dispose_types VARCHAR(120) DEFAULT NULL COMMENT '可接收垃圾类型，逗号分隔',
  manager VARCHAR(30) DEFAULT NULL,
  phone VARCHAR(20) DEFAULT NULL,
  image VARCHAR(200) DEFAULT NULL,
  status TINYINT DEFAULT 1 COMMENT '1 启用 0 停用',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0
) ENGINE=InnoDB COMMENT='处置场';

-- 线路
CREATE TABLE route (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  route_code VARCHAR(30) NOT NULL UNIQUE,
  route_name VARCHAR(60) NOT NULL,
  area VARCHAR(50) NOT NULL,
  distance_km DECIMAL(8,2) DEFAULT 0 COMMENT '线路里程',
  stop_count INT DEFAULT 0,
  status TINYINT DEFAULT 1,
  remark VARCHAR(200) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0
) ENGINE=InnoDB COMMENT='清运线路';

-- 收集点
CREATE TABLE collection_point (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  point_code VARCHAR(50) NOT NULL UNIQUE COMMENT '点位编码，业务唯一',
  point_name VARCHAR(80) NOT NULL,
  area VARCHAR(50) NOT NULL COMMENT '所属区域',
  address VARCHAR(150) DEFAULT NULL,
  waste_type VARCHAR(20) NOT NULL COMMENT '垃圾类型（字典 waste_type）',
  capacity DECIMAL(8,2) NOT NULL COMMENT '容量(吨)',
  current_load DECIMAL(8,2) NOT NULL DEFAULT 0 COMMENT '当前装载量(吨)',
  load_rate INT NOT NULL DEFAULT 0 COMMENT '当前满载度 %，后端计算',
  org_id BIGINT DEFAULT NULL COMMENT '责任单位',
  manager VARCHAR(30) DEFAULT NULL COMMENT '负责人',
  manager_phone VARCHAR(20) DEFAULT NULL,
  last_clear_time DATETIME DEFAULT NULL,
  longitude DECIMAL(10,6) DEFAULT NULL,
  latitude DECIMAL(10,6) DEFAULT NULL,
  cover_image VARCHAR(200) DEFAULT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'NORMAL' COMMENT 'NORMAL/OVERFLOW/DISABLED',
  version INT DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0,
  KEY idx_point_area (area),
  KEY idx_point_status (status)
) ENGINE=InnoDB COMMENT='垃圾收集点';

-- 车辆
CREATE TABLE vehicle (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  plate_no VARCHAR(20) NOT NULL UNIQUE,
  vehicle_type VARCHAR(20) NOT NULL COMMENT '压缩式/后装式/密闭罐式/勾臂式',
  load_capacity DECIMAL(8,2) NOT NULL COMMENT '载重(吨)',
  waste_types VARCHAR(120) DEFAULT NULL COMMENT '可收运类型',
  annual_check_date DATE DEFAULT NULL,
  mileage INT DEFAULT 0 COMMENT '累计里程 km',
  status VARCHAR(20) NOT NULL DEFAULT 'IDLE' COMMENT 'IDLE/BUSY/MAINTAIN/DISABLED',
  image VARCHAR(200) DEFAULT NULL,
  remark VARCHAR(200) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0
) ENGINE=InnoDB COMMENT='清运车辆';

-- 司机
CREATE TABLE driver (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  driver_no VARCHAR(30) NOT NULL UNIQUE,
  name VARCHAR(30) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  license_no VARCHAR(40) NOT NULL COMMENT '驾驶证号',
  license_type VARCHAR(10) NOT NULL COMMENT '准驾车型',
  license_expire DATE NOT NULL,
  vehicle_id BIGINT DEFAULT NULL COMMENT '常驾车辆',
  avatar VARCHAR(200) DEFAULT NULL,
  status TINYINT DEFAULT 1 COMMENT '1 在岗 0 离岗',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0
) ENGINE=InnoDB COMMENT='司机档案';

-- 周期计划
CREATE TABLE collection_plan (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  plan_code VARCHAR(40) NOT NULL UNIQUE,
  point_id BIGINT NOT NULL,
  route_id BIGINT DEFAULT NULL,
  waste_type VARCHAR(20) NOT NULL,
  frequency VARCHAR(20) NOT NULL COMMENT 'DAILY/EVERY_2_DAYS/WEEKLY',
  weekday TINYINT DEFAULT NULL COMMENT 'WEEKLY 时的星期 1-7',
  estimated_weight DECIMAL(8,2) NOT NULL,
  next_date DATE NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ON' COMMENT 'ON/OFF',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  deleted TINYINT DEFAULT 0,
  KEY idx_plan_point (point_id)
) ENGINE=InnoDB COMMENT='周期清运计划';

-- 临时报满
CREATE TABLE overflow_report (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  report_no VARCHAR(40) NOT NULL UNIQUE,
  point_id BIGINT NOT NULL,
  overflow_level VARCHAR(20) NOT NULL COMMENT 'LIGHT/OBVIOUS/SERIOUS',
  estimated_weight DECIMAL(8,2) NOT NULL,
  image VARCHAR(200) NOT NULL COMMENT '现场图片相对路径',
  description VARCHAR(300) DEFAULT NULL,
  urgency_score DECIMAL(6,2) DEFAULT 0 COMMENT '紧急度（含满载度与滞留）',
  reporter_id BIGINT DEFAULT NULL,
  report_time DATETIME NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT 'PENDING/DISPATCHED/DONE/CANCELED',
  order_id BIGINT DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_of_status (status)
) ENGINE=InnoDB COMMENT='临时报满';

-- 投诉
CREATE TABLE complaint (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  point_id BIGINT NOT NULL,
  content VARCHAR(300) NOT NULL,
  level VARCHAR(10) NOT NULL COMMENT 'LOW/MID/HIGH',
  source VARCHAR(30) DEFAULT '热线',
  handle_status VARCHAR(20) DEFAULT 'PENDING' COMMENT 'PENDING/DONE',
  happen_time DATETIME NOT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='投诉记录';

-- 清运任务（派单）
CREATE TABLE dispatch_order (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_no VARCHAR(40) NOT NULL UNIQUE,
  order_type VARCHAR(20) NOT NULL COMMENT 'PLAN 周期 / URGENT 紧急 / MERGE 合并',
  route_id BIGINT DEFAULT NULL,
  vehicle_id BIGINT DEFAULT NULL,
  driver_id BIGINT DEFAULT NULL,
  dispose_site_id BIGINT DEFAULT NULL,
  point_summary VARCHAR(200) DEFAULT NULL COMMENT '合并点摘要',
  stop_count INT DEFAULT 1,
  plan_time DATETIME NOT NULL COMMENT '计划到场时间',
  dispatch_time DATETIME DEFAULT NULL COMMENT '实际派单时间',
  estimated_weight DECIMAL(8,2) NOT NULL COMMENT '预估总重',
  actual_weight DECIMAL(8,2) DEFAULT NULL COMMENT '各点实际合计',
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING_DISPATCH'
      COMMENT 'PENDING_DISPATCH 待派车/ACCEPTED 已接单/RUNNING 清运中/PENDING_CONFIRM 待确认/DONE 已完成/CANCELED 已取消/ABNORMAL 异常',
  priority_score DECIMAL(6,2) DEFAULT NULL COMMENT '联合调度得分',
  priority_grade VARCHAR(10) DEFAULT NULL COMMENT 'P1/P2/P3/NONE',
  dispatcher_id BIGINT DEFAULT NULL,
  reason VARCHAR(200) DEFAULT NULL COMMENT '取消/改派/拒接原因',
  create_by BIGINT DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  version INT DEFAULT 0,
  deleted TINYINT DEFAULT 0,
  KEY idx_order_status (status),
  KEY idx_order_driver (driver_id),
  KEY idx_order_plan_time (plan_time)
) ENGINE=InnoDB COMMENT='清运任务';

-- 任务站点
CREATE TABLE route_stop (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT NOT NULL,
  point_id BIGINT NOT NULL,
  seq INT NOT NULL COMMENT '站点顺序',
  plan_arrive DATETIME DEFAULT NULL,
  arrive_time DATETIME DEFAULT NULL COMMENT '实际到场',
  leave_time DATETIME DEFAULT NULL COMMENT '实际离场',
  estimated_weight DECIMAL(8,2) DEFAULT 0,
  actual_weight DECIMAL(8,2) DEFAULT NULL,
  site_image VARCHAR(200) DEFAULT NULL COMMENT '现场图片',
  status VARCHAR(20) NOT NULL DEFAULT 'WAITING' COMMENT 'WAITING/ARRIVED/DONE/SKIPPED',
  remark VARCHAR(200) DEFAULT NULL,
  KEY idx_stop_order (order_id)
) ENGINE=InnoDB COMMENT='任务站点';

-- 称重/交接
CREATE TABLE weighing_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  record_no VARCHAR(40) NOT NULL UNIQUE,
  order_id BIGINT NOT NULL,
  dispose_site_id BIGINT NOT NULL,
  in_weight DECIMAL(8,2) NOT NULL COMMENT '进场重量(吨)',
  out_weight DECIMAL(8,2) NOT NULL COMMENT '出场重量(吨)',
  net_weight DECIMAL(8,2) NOT NULL COMMENT '净重=进-出',
  dispose_type VARCHAR(20) NOT NULL COMMENT '填埋/焚烧发电/资源化利用',
  weighing_image VARCHAR(200) DEFAULT NULL COMMENT '称重单图片',
  weigh_time DATETIME NOT NULL,
  deviation DECIMAL(6,2) DEFAULT 0 COMMENT '净重与各点合计偏差 %',
  review_status VARCHAR(20) NOT NULL DEFAULT 'PASS' COMMENT 'PASS/REVIEW 复核',
  review_note VARCHAR(200) DEFAULT NULL,
  reviewer VARCHAR(30) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_weigh_order (order_id)
) ENGINE=InnoDB COMMENT='处置称重交接';

-- 异常
CREATE TABLE exception_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  exception_no VARCHAR(40) NOT NULL UNIQUE,
  order_id BIGINT DEFAULT NULL,
  point_id BIGINT DEFAULT NULL,
  type VARCHAR(20) NOT NULL COMMENT 'VEHICLE_FAULT/UNREACHABLE/OVERLOAD/MISS_STOP/OTHER',
  level VARCHAR(10) NOT NULL COMMENT 'LOW/MID/HIGH',
  description VARCHAR(300) NOT NULL,
  image VARCHAR(200) DEFAULT NULL,
  reporter VARCHAR(30) DEFAULT NULL,
  handler VARCHAR(30) DEFAULT NULL,
  handle_result VARCHAR(300) DEFAULT NULL COMMENT '处理结论（改派/恢复/终止）',
  status VARCHAR(20) NOT NULL DEFAULT 'OPEN' COMMENT 'OPEN/HANDLING/CLOSED',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_ex_status (status)
) ENGINE=InnoDB COMMENT='异常记录';

-- 车辆保养
CREATE TABLE vehicle_maintenance (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  vehicle_id BIGINT NOT NULL,
  maintain_type VARCHAR(20) NOT NULL COMMENT '常规保养/年检/维修',
  maintain_date DATE NOT NULL,
  mileage INT NOT NULL COMMENT '保养时里程',
  next_date DATE DEFAULT NULL COMMENT '下次保养日期',
  next_mileage INT DEFAULT NULL COMMENT '下次保养里程',
  cost DECIMAL(10,2) DEFAULT 0,
  status VARCHAR(20) NOT NULL DEFAULT 'DONE' COMMENT 'DONE/DUE 预警/ING 保养中',
  remark VARCHAR(200) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='车辆保养记录';

-- 附件
CREATE TABLE attachment (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  biz_type VARCHAR(30) NOT NULL COMMENT '业务类型',
  biz_id BIGINT NOT NULL,
  file_name VARCHAR(160) NOT NULL,
  file_path VARCHAR(200) NOT NULL COMMENT '相对路径，不存外部 URL',
  file_size BIGINT DEFAULT 0,
  uploader VARCHAR(30) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_att_biz (biz_type, biz_id)
) ENGINE=InnoDB COMMENT='附件';

-- 流转日志
CREATE TABLE flow_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  biz_type VARCHAR(30) NOT NULL DEFAULT 'DISPATCH',
  biz_id BIGINT NOT NULL,
  biz_no VARCHAR(40) DEFAULT NULL,
  from_status VARCHAR(20) DEFAULT NULL,
  to_status VARCHAR(20) DEFAULT NULL,
  action VARCHAR(40) NOT NULL COMMENT '创建/派车/接单/到场/完成/交接/取消/改派/复核',
  reason VARCHAR(200) DEFAULT NULL,
  operator VARCHAR(30) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_flow_biz (biz_type, biz_id)
) ENGINE=InnoDB COMMENT='业务流转日志';

-- 创新点：调度规则
CREATE TABLE dispatch_rule (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  rule_name VARCHAR(60) NOT NULL,
  version INT NOT NULL,
  w_load INT NOT NULL COMMENT '满载度权重',
  w_stay INT NOT NULL COMMENT '滞留时长权重',
  w_complaint INT NOT NULL COMMENT '投诉次数权重',
  w_capacity INT NOT NULL COMMENT '车辆剩余容量权重',
  w_distance INT NOT NULL COMMENT '点位距离权重',
  w_type_match INT NOT NULL COMMENT '垃圾类型匹配权重',
  threshold_p1 INT DEFAULT 85,
  threshold_p2 INT DEFAULT 65,
  threshold_p3 INT DEFAULT 45,
  review_threshold INT DEFAULT 5 COMMENT '净重复核阈值 %',
  enabled TINYINT DEFAULT 0,
  effective_time DATETIME DEFAULT NULL,
  create_by VARCHAR(30) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB COMMENT='调度规则版本';

-- 创新点：计算留痕
CREATE TABLE dispatch_score (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id BIGINT NOT NULL,
  rule_id BIGINT NOT NULL,
  rule_version INT NOT NULL,
  snapshot TEXT COMMENT '输入快照 JSON',
  v_load DECIMAL(8,2) DEFAULT NULL,
  v_stay DECIMAL(8,2) DEFAULT NULL,
  v_complaint INT DEFAULT NULL,
  v_capacity DECIMAL(8,2) DEFAULT NULL,
  v_distance DECIMAL(8,2) DEFAULT NULL,
  v_type_match INT DEFAULT NULL,
  s_load DECIMAL(6,2) DEFAULT 0,
  s_stay DECIMAL(6,2) DEFAULT 0,
  s_complaint DECIMAL(6,2) DEFAULT 0,
  s_capacity DECIMAL(6,2) DEFAULT 0,
  s_distance DECIMAL(6,2) DEFAULT 0,
  s_type_match DECIMAL(6,2) DEFAULT 0,
  total_score DECIMAL(6,2) NOT NULL,
  grade VARCHAR(10) NOT NULL COMMENT 'P1/P2/P3/NONE',
  factors VARCHAR(500) DEFAULT NULL COMMENT '主要影响因素',
  unmet VARCHAR(500) DEFAULT NULL COMMENT '未满足条件',
  improve VARCHAR(500) DEFAULT NULL COMMENT '可改进项',
  adopted TINYINT DEFAULT 0 COMMENT '是否采纳推荐',
  manual_adjust TINYINT DEFAULT 0 COMMENT '人工是否调整',
  adjust_reason VARCHAR(200) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_score_order (order_id)
) ENGINE=InnoDB COMMENT='调度计算留痕';

INSERT INTO sys_org (id, org_name, org_type, area, leader, phone, sort, status, create_time, deleted) VALUES
(1, '城南环卫所', '环卫所', '城南街道', '周建明', '0571-88230001', 1, 1, '2026-05-17 09:12:19', 0),
(2, '锦绣物业管理处', '物业', '城南街道', '王秀兰', '0571-88230012', 2, 1, '2026-05-20 09:12:15', 0),
(3, '老城环卫所', '环卫所', '老城街道', '张德海', '0571-88230003', 3, 1, '2026-05-23 09:12:48', 0),
(4, '滨江市容管理处', '环卫所', '滨江片区', '陈志远', '0571-88230004', 4, 1, '2026-05-26 09:12:46', 0),
(5, '高新园区服务中心', '园区', '高新片区', '刘敏', '0571-88230005', 5, 1, '2026-05-29 09:12:24', 0),
(6, '城北乡镇环卫站', '乡镇', '城北乡镇', '赵国强', '0571-88230006', 6, 1, '2026-06-01 09:12:04', 0);

INSERT INTO sys_role (id, role_code, role_name, data_scope, remark, create_time) VALUES
(1, 'ADMIN', '运营管理员', 'ALL', '全部数据范围，维护基础档案与报表', '2026-05-04 10:00:32'),
(2, 'DISPATCHER', '调度员', 'ORG', '调度范围内的任务与异常', '2026-05-04 10:00:02'),
(3, 'POINT', '收集点管理员', 'SELF', '仅本点位报量与派单查看', '2026-05-04 10:00:13'),
(4, 'DRIVER', '司机', 'SELF', '仅本人任务', '2026-05-04 10:00:15');

INSERT INTO sys_menu (id, parent_id, menu_name, path, icon, menu_type, perm, sort, visible, create_time) VALUES
(1, 0, '运营总览', NULL, NULL, 'M', NULL, 1, 1, '2026-05-06 10:00:30'),
(2, 1, '环卫运营看板', '/dashboard', 'dashboard', 'M', 'dashboard:view', 2, 1, '2026-05-06 10:00:14'),
(3, 0, '基础档案', NULL, NULL, 'M', NULL, 3, 2, '2026-05-06 10:00:40'),
(4, 3, '收集点管理', '/point', 'point', 'M', 'point:list', 4, 1, '2026-05-06 10:00:10'),
(5, 4, '新增收集点', NULL, NULL, 'B', 'point:add', 5, 1, '2026-05-06 10:00:06'),
(6, 4, '编辑收集点', NULL, NULL, 'B', 'point:edit', 6, 1, '2026-05-06 10:00:58'),
(7, 4, '删除收集点', NULL, NULL, 'B', 'point:delete', 7, 1, '2026-05-06 10:00:49'),
(8, 3, '车辆档案', '/vehicle', 'truck', 'M', 'vehicle:list', 8, 2, '2026-05-06 10:00:36'),
(9, 8, '编辑车辆', NULL, NULL, 'B', 'vehicle:edit', 9, 1, '2026-05-06 10:00:55'),
(10, 3, '司机档案', '/driver', 'driver', 'M', 'driver:list', 10, 3, '2026-05-06 10:00:48'),
(11, 3, '线路与处置场', '/route', 'route', 'M', 'route:list', 11, 4, '2026-05-06 10:00:48'),
(12, 0, '调度台账', NULL, NULL, 'M', NULL, 12, 3, '2026-05-06 10:00:37'),
(13, 12, '清运调度台', '/dispatch', 'dispatch', 'M', 'dispatch:list', 13, 1, '2026-05-06 10:00:02'),
(14, 13, '派车', NULL, NULL, 'B', 'dispatch:assign', 14, 1, '2026-05-06 10:00:17'),
(15, 13, '改派', NULL, NULL, 'B', 'dispatch:reassign', 15, 2, '2026-05-06 10:00:14'),
(16, 12, '临时报满', '/overflow', 'overflow', 'M', 'overflow:list', 16, 2, '2026-05-06 10:00:05'),
(17, 16, '上报报满', NULL, NULL, 'B', 'overflow:add', 17, 1, '2026-05-06 10:00:14'),
(18, 12, '称重交接', '/weighing', 'weigh', 'M', 'weigh:list', 18, 3, '2026-05-06 10:00:36'),
(19, 18, '确认交接', NULL, NULL, 'B', 'weigh:confirm', 19, 1, '2026-05-06 10:00:30'),
(20, 12, '异常处理', NULL, NULL, 'B', 'exception:list', 20, 4, '2026-05-06 10:00:11'),
(21, 20, '处理异常', NULL, NULL, 'B', 'exception:handle', 21, 1, '2026-05-06 10:00:49'),
(22, 12, '车辆保养', '/maintenance', 'wrench', 'M', 'maintain:list', 22, 5, '2026-05-06 10:00:24'),
(23, 0, '分析与配置', NULL, NULL, 'M', NULL, 23, 4, '2026-05-06 10:00:55'),
(24, 23, '调度规则配置', '/rule', 'rule', 'M', 'rule:config', 24, 1, '2026-05-06 10:00:42'),
(25, 24, '保存规则', NULL, NULL, 'B', 'rule:save', 25, 1, '2026-05-06 10:00:23'),
(26, 23, '计算留痕', '/score', 'report', 'M', 'score:list', 26, 2, '2026-05-06 10:00:51'),
(27, 23, '统计报表', '/report', 'report', 'M', 'report:view', 27, 3, '2026-05-06 10:00:39'),
(28, 0, '系统管理', NULL, NULL, 'M', NULL, 28, 5, '2026-05-06 10:00:15'),
(29, 28, '用户管理', '/user', 'user', 'M', 'user:list', 29, 1, '2026-05-06 10:00:06'),
(30, 28, '角色管理', '/role', 'role', 'M', 'role:list', 30, 2, '2026-05-06 10:00:02'),
(31, 28, '菜单管理', '/menu', 'menu', 'M', 'menu:list', 31, 3, '2026-05-06 10:00:27'),
(32, 28, '为角色分配菜单', NULL, NULL, 'B', 'role:assign', 32, 4, '2026-05-06 10:00:10'),
(33, 0, '个人中心', NULL, NULL, 'M', NULL, 33, 6, '2026-05-06 10:00:40'),
(34, 33, '我的任务', '/my-task', 'dispatch', 'M', 'task:mine', 34, 1, '2026-05-06 10:00:26'),
(35, 33, '我的点位', '/my-point', 'point', 'M', 'point:mine', 35, 2, '2026-05-06 10:00:31');

UPDATE sys_menu SET visible = 0 WHERE menu_name = '菜单管理';

-- 菜单可见性统一：除「菜单管理」外全部 visible=1；按钮类（menu_type=B）由后端过滤，不进侧边栏
UPDATE sys_menu SET visible = CASE WHEN menu_name = '菜单管理' THEN 0 ELSE 1 END;
-- 异常处理原被误标为按钮类型，修正为菜单类型，否则侧边栏缺失该页
UPDATE sys_menu SET menu_type = 'M' WHERE menu_name = '异常处理';
-- 周期计划菜单项原数据缺失，补齐并授权给运营管理员、调度员
INSERT IGNORE INTO sys_menu (id, parent_id, menu_name, path, icon, menu_type, perm, sort, visible, create_time)
VALUES (36, 12, '周期计划', '/plan', 'calendar', 'M', 'plan:list', 17, 1, NOW());
INSERT IGNORE INTO sys_role_menu (role_id, menu_id) VALUES (1, 36), (2, 36);

INSERT INTO sys_role_menu (id, role_id, menu_id) VALUES
(1, 1, 1),
(2, 1, 2),
(3, 1, 3),
(4, 1, 4),
(5, 1, 5),
(6, 1, 6),
(7, 1, 7),
(8, 1, 8),
(9, 1, 9),
(10, 1, 10),
(11, 1, 11),
(12, 1, 12),
(13, 1, 13),
(14, 1, 14),
(15, 1, 15),
(16, 1, 16),
(17, 1, 17),
(18, 1, 18),
(19, 1, 19),
(20, 1, 20),
(21, 1, 21),
(22, 1, 22),
(23, 1, 23),
(24, 1, 24),
(25, 1, 25),
(26, 1, 26),
(27, 1, 27),
(28, 1, 28),
(29, 1, 29),
(30, 1, 30),
(31, 1, 31),
(32, 1, 32),
(33, 1, 33),
(34, 1, 34),
(35, 2, 1),
(36, 2, 2),
(37, 2, 3),
(38, 2, 4),
(39, 2, 12),
(40, 2, 13),
(41, 2, 14),
(42, 2, 15),
(43, 2, 16),
(44, 2, 17),
(45, 2, 18),
(46, 2, 19),
(47, 2, 20),
(48, 2, 21),
(49, 2, 22),
(50, 2, 23),
(51, 2, 24),
(52, 2, 25),
(53, 2, 26),
(54, 2, 27),
(55, 2, 33),
(56, 2, 34),
(57, 3, 1),
(58, 3, 2),
(59, 3, 3),
(60, 3, 4),
(61, 3, 5),
(62, 3, 12),
(63, 3, 16),
(64, 3, 17),
(65, 3, 18),
(66, 3, 33),
(67, 3, 34),
(68, 3, 35),
(69, 4, 33),
(70, 4, 35);

INSERT INTO dispose_site (id, site_code, site_name, address, capacity, dispose_types, manager, phone, image, status, create_time, deleted) VALUES
(1, 'DS-001', '城南综合处置场', '城南街道疏港路 88 号', 800.0, '生活垃圾,建筑垃圾,大件垃圾', '孙志刚', '0571-88230101', '/uploads/seed/dispose/02.jpg', 1, '2026-05-13 10:20:34', 0),
(2, 'DS-002', '城西焚烧发电厂', '老城街道工业园 12 号', 600.0, '生活垃圾,园林绿化', '吴建国', '0571-88230102', '/uploads/seed/dispose/01.jpg', 1, '2026-05-17 10:20:21', 0),
(3, 'DS-003', '滨江资源化利用中心', '滨江片区临江路 5 号', 300.0, '建筑垃圾,大件垃圾', '郑海涛', '0571-88230103', '/uploads/seed/dispose/02.jpg', 1, '2026-05-21 10:20:29', 0),
(4, 'DS-004', '高新餐厨处理站', '高新片区科创大道 66 号', 200.0, '餐厨垃圾', '刘敏', '0571-88230104', '/uploads/seed/dispose/01.jpg', 1, '2026-05-25 10:20:23', 0),
(5, 'DS-005', '城北填埋场', '城北乡镇北环路 21 号', 500.0, '生活垃圾,建筑垃圾', '赵国强', '0571-88230105', '/uploads/seed/dispose/02.jpg', 1, '2026-05-29 10:20:24', 0);

INSERT INTO route (id, route_code, route_name, area, distance_km, stop_count, status, remark, create_time, deleted) VALUES
(1, 'R-01', '老城环线', '老城街道', 18.6, 5, 1, '线路 R-01 覆盖 老城街道 主要收集点', '2026-05-14 11:05:23', 0),
(2, 'R-02', '城南环线', '城南街道', 22.4, 6, 1, '线路 R-02 覆盖 城南街道 主要收集点', '2026-05-16 11:05:41', 0),
(3, 'R-03', '城北乡镇线', '城北乡镇', 34.2, 5, 1, '线路 R-03 覆盖 城北乡镇 主要收集点', '2026-05-18 11:05:25', 0),
(4, 'R-04', '滨江线', '滨江片区', 19.8, 4, 1, '线路 R-04 覆盖 滨江片区 主要收集点', '2026-05-20 11:05:23', 0),
(5, 'R-05', '高新线', '高新片区', 16.5, 4, 1, '线路 R-05 覆盖 高新片区 主要收集点', '2026-05-22 11:05:07', 0),
(6, 'R-06', '城南东线', '城南街道', 14.2, 3, 1, '线路 R-06 覆盖 城南街道 主要收集点', '2026-05-24 11:05:35', 0);

INSERT INTO collection_point (id, point_code, point_name, area, address, waste_type, capacity, current_load, load_rate, org_id, manager, manager_phone, last_clear_time, longitude, latitude, cover_image, status, version, create_time, update_time, deleted) VALUES
(1, 'CP-2026-0031', '城南农贸市场东门站', '城南街道', '城南街道农贸市场东门', '生活垃圾', 8.00, 5.44, 68, 1, '李国庆', '138****2210', '2026-10-29 05:27:04', 120.157, 30.276, '/uploads/seed/point/02.jpg', 'NORMAL', 2, '2026-05-17 09:30:24', '2026-10-29 05:27:04', 0),
(2, 'CP-2026-0032', '锦绣花园小区北门站', '城南街道', '锦绣花园北门内侧', '生活垃圾', 6.00, 4.79, 80, 2, '王秀兰', '139****6602', '2026-10-22 08:58:42', 120.164, 30.272, '/uploads/seed/point/03.jpg', 'NORMAL', 1, '2026-05-20 09:30:08', '2026-10-22 08:58:42', 0),
(3, 'CP-2026-0033', '第三小学后街站', '老城街道', '老城街道后街 18 号', '生活垃圾', 4.00, 1.09, 27, 3, '张德海', '137****8891', '2026-10-28 06:10:32', 120.171, 30.268, '/uploads/seed/point/04.jpg', 'NORMAL', 1, '2026-05-23 09:30:55', '2026-10-28 06:10:32', 0),
(4, 'CP-2026-0034', '滨江路建材市场站', '滨江片区', '滨江路建材市场西侧', '建筑垃圾', 12.00, 3.00, 25, 4, '陈志远', '136****3345', '2026-10-31 08:54:40', 120.178, 30.264, '/uploads/seed/point/05.jpg', 'NORMAL', 2, '2026-05-26 09:30:25', '2026-10-31 08:54:40', 0),
(5, 'CP-2026-0035', '高新科技园 B 区站', '高新片区', '科创大道 B 区 3 号楼旁', '餐厨垃圾', 5.00, 2.96, 59, 5, '刘敏', '135****7723', '2026-10-28 06:21:36', 120.185, 30.26, '/uploads/seed/point/06.jpg', 'NORMAL', 1, '2026-05-29 09:30:13', '2026-10-28 06:21:36', 0),
(6, 'CP-2026-0036', '城北乡镇卫生院站', '城北乡镇', '城北乡镇卫生院后院', '生活垃圾', 3.00, 1.61, 54, 6, '赵国强', '133****1180', '2026-10-23 07:32:51', 120.192, 30.256, '/uploads/seed/point/01.jpg', 'NORMAL', 0, '2026-06-01 09:30:55', '2026-10-23 07:32:51', 0),
(7, 'CP-2026-0037', '老城文化广场站', '老城街道', '文化广场东南角', '园林绿化', 6.00, 3.05, 51, 3, '孙丽华', '138****5567', '2026-10-29 05:16:02', 120.199, 30.252, '/uploads/seed/point/02.jpg', 'DISABLED', 0, '2026-06-04 09:30:45', '2026-10-29 05:16:02', 0),
(8, 'CP-2026-0038', '滨江花园西区站', '滨江片区', '滨江花园西区 7 幢旁', '生活垃圾', 8.00, 7.16, 90, 4, '郑海涛', '139****9902', '2026-10-30 05:46:42', 120.206, 30.248, '/uploads/seed/point/03.jpg', 'OVERFLOW', 0, '2026-06-07 09:30:18', '2026-10-30 05:46:42', 0),
(9, 'CP-2026-0039', '城南小学北门站', '城南街道', '城南小学北门', '生活垃圾', 4.00, 3.39, 85, 1, '李国庆', '138****2210', '2026-10-26 08:56:46', 120.213, 30.244, '/uploads/seed/point/04.jpg', 'NORMAL', 2, '2026-06-10 09:30:42', '2026-10-26 08:56:46', 0),
(10, 'CP-2026-0040', '锦绣花园东门站', '城南街道', '锦绣花园东门车库口', '生活垃圾', 6.00, 4.72, 79, 2, '王秀兰', '139****6602', '2026-10-27 08:19:14', 120.22, 30.24, '/uploads/seed/point/05.jpg', 'NORMAL', 2, '2026-06-13 09:30:38', '2026-10-27 08:19:14', 0),
(11, 'CP-2026-0041', '老城菜市场西站', '老城街道', '老城菜市场西侧巷道', '生活垃圾', 5.00, 2.18, 44, 3, '张德海', '137****8891', '2026-10-29 12:44:29', 120.227, 30.236, '/uploads/seed/point/06.jpg', 'NORMAL', 0, '2026-06-16 09:30:03', '2026-10-29 12:44:29', 0),
(12, 'CP-2026-0042', '老城医院后门站', '老城街道', '老城医院后勤通道', '生活垃圾', 4.00, 0.77, 19, 3, '孙丽华', '138****5567', '2026-10-23 17:31:49', 120.234, 30.232, '/uploads/seed/point/01.jpg', 'NORMAL', 2, '2026-06-19 09:30:04', '2026-10-23 17:31:49', 0),
(13, 'CP-2026-0043', '滨江写字楼群站', '滨江片区', '滨江大道 100 号楼下', '生活垃圾', 6.00, 1.77, 30, 4, '陈志远', '136****3345', '2026-10-22 08:35:38', 120.241, 30.228, '/uploads/seed/point/02.jpg', 'NORMAL', 2, '2026-06-22 09:30:05', '2026-10-22 08:35:38', 0),
(14, 'CP-2026-0044', '滨江装饰城站', '滨江片区', '装饰城北门停车场', '建筑垃圾', 10.00, 9.53, 95, 4, '郑海涛', '139****9902', '2026-10-23 09:26:17', 120.248, 30.224, '/uploads/seed/point/03.jpg', 'OVERFLOW', 3, '2026-06-25 09:30:13', '2026-10-23 09:26:17', 0),
(15, 'CP-2026-0045', '高新产品园 A 区站', '高新片区', '产品园 A 区食堂后', '餐厨垃圾', 5.00, 1.16, 23, 5, '刘敏', '135****7723', '2026-10-22 14:16:45', 120.255, 30.22, '/uploads/seed/point/04.jpg', 'NORMAL', 1, '2026-06-28 09:30:25', '2026-10-22 14:16:45', 0),
(16, 'CP-2026-0046', '高新宿舍区站', '高新片区', '高新宿舍区 2 号楼旁', '生活垃圾', 6.00, 4.82, 80, 5, '刘敏', '135****7723', '2026-10-29 17:04:52', 120.262, 30.216, '/uploads/seed/point/05.jpg', 'NORMAL', 2, '2026-07-01 09:30:31', '2026-10-29 17:04:52', 0),
(17, 'CP-2026-0047', '城北农贸集市站', '城北乡镇', '城北集市北侧', '生活垃圾', 5.00, 2.87, 57, 6, '赵国强', '133****1180', '2026-10-30 18:49:18', 120.269, 30.212, '/uploads/seed/point/06.jpg', 'NORMAL', 3, '2026-07-04 09:30:49', '2026-10-30 18:49:18', 0),
(18, 'CP-2026-0048', '城北中学站', '城北乡镇', '城北中学围墙外', '生活垃圾', 4.00, 1.70, 42, 6, '赵国强', '133****1180', '2026-10-28 10:46:25', 120.276, 30.208, '/uploads/seed/point/01.jpg', 'NORMAL', 0, '2026-07-07 09:30:02', '2026-10-28 10:46:25', 0),
(19, 'CP-2026-0049', '城南工业园站', '城南街道', '工业园纬三路', '建筑垃圾', 14.00, 4.92, 35, 1, '李国庆', '138****2210', '2026-10-23 06:54:15', 120.283, 30.204, '/uploads/seed/point/02.jpg', 'NORMAL', 2, '2026-07-10 09:30:15', '2026-10-23 06:54:15', 0),
(20, 'CP-2026-0050', '滨江公园东门站', '滨江片区', '滨江公园东门', '园林绿化', 5.00, 1.31, 26, 4, '郑海涛', '139****9902', '2026-10-22 10:48:00', 120.29, 30.2, '/uploads/seed/point/03.jpg', 'NORMAL', 2, '2026-07-13 09:30:32', '2026-10-22 10:48:00', 0);

INSERT INTO vehicle (id, plate_no, vehicle_type, load_capacity, waste_types, annual_check_date, mileage, status, image, remark, create_time, deleted) VALUES
(1, '粤A·D8821', '压缩式', 8.0, '生活垃圾,园林绿化', '2026-11-12', 111189, 'BUSY', '/uploads/seed/vehicle/02.jpg', '车辆 粤A·D8821，压缩式，额定载重 8.0 吨', '2026-05-18 08:15:38', 0),
(2, '粤A·D8836', '后装式', 6.0, '生活垃圾', '2026-11-08', 90718, 'IDLE', '/uploads/seed/vehicle/03.jpg', '车辆 粤A·D8836，后装式，额定载重 6.0 吨', '2026-05-20 08:15:19', 0),
(3, '粤A·D8850', '压缩式', 10.0, '生活垃圾,建筑垃圾', '2026-11-20', 49093, 'IDLE', '/uploads/seed/vehicle/01.jpg', '车辆 粤A·D8850，压缩式，额定载重 10.0 吨', '2026-05-22 08:15:56', 0),
(4, '粤A·D8862', '密闭罐式', 5.0, '餐厨垃圾', '2026-12-06', 68008, 'BUSY', '/uploads/seed/vehicle/02.jpg', '车辆 粤A·D8862，密闭罐式，额定载重 5.0 吨', '2026-05-24 08:15:52', 0),
(5, '粤A·D8875', '后装式', 6.0, '生活垃圾,园林绿化', '2026-11-03', 65485, 'MAINTAIN', '/uploads/seed/vehicle/03.jpg', '车辆 粤A·D8875，后装式，额定载重 6.0 吨', '2026-05-26 08:15:02', 0),
(6, '粤A·D8881', '勾臂式', 12.0, '建筑垃圾,大件垃圾', '2026-12-24', 92967, 'IDLE', '/uploads/seed/vehicle/01.jpg', '车辆 粤A·D8881，勾臂式，额定载重 12.0 吨', '2026-05-28 08:15:43', 0),
(7, '粤A·D8890', '压缩式', 8.0, '生活垃圾', '2026-10-25', 80445, 'IDLE', '/uploads/seed/vehicle/02.jpg', '车辆 粤A·D8890，压缩式，额定载重 8.0 吨', '2026-05-30 08:15:46', 0),
(8, '粤A·D8903', '密闭罐式', 5.0, '餐厨垃圾', '2027-01-27', 34324, 'BUSY', '/uploads/seed/vehicle/03.jpg', '车辆 粤A·D8903，密闭罐式，额定载重 5.0 吨', '2026-06-01 08:15:41', 0),
(9, '粤A·D8915', '后装式', 6.0, '生活垃圾', '2026-11-15', 138291, 'IDLE', '/uploads/seed/vehicle/01.jpg', '车辆 粤A·D8915，后装式，额定载重 6.0 吨', '2026-06-03 08:15:35', 0),
(10, '粤A·D8927', '勾臂式', 12.0, '建筑垃圾,大件垃圾', '2026-12-11', 30507, 'DISABLED', '/uploads/seed/vehicle/02.jpg', '车辆 粤A·D8927，勾臂式，额定载重 12.0 吨', '2026-06-05 08:15:47', 0);

INSERT INTO driver (id, driver_no, name, phone, license_no, license_type, license_expire, vehicle_id, avatar, status, create_time, deleted) VALUES
(1, 'D-1001', '陈伟强', '138****1234', '3301**********1234', 'A2', '2029-05-18', 1, '/uploads/seed/avatar/02.jpg', 1, '2026-05-22 09:00:46', 0),
(2, 'D-1002', '黄志明', '139****5678', '3301**********5678', 'B2', '2028-11-02', 2, '/uploads/seed/avatar/03.jpg', 1, '2026-05-25 09:00:16', 0),
(3, 'D-1003', '王建军', '137****9012', '3301**********9012', 'A2', '2027-08-25', 3, '/uploads/seed/avatar/04.jpg', 1, '2026-05-28 09:00:18', 0),
(4, 'D-1004', '刘海涛', '136****3456', '3301**********3456', 'B2', '2030-01-14', 4, '/uploads/seed/avatar/05.jpg', 1, '2026-05-31 09:00:43', 0),
(5, 'D-1005', '李国强', '135****7890', '3301**********7890', 'A2', '2026-12-09', 5, '/uploads/seed/avatar/06.jpg', 1, '2026-06-03 09:00:15', 0),
(6, 'D-1006', '徐立新', '133****2345', '3301**********2345', 'B2', '2029-03-21', 6, '/uploads/seed/avatar/01.jpg', 1, '2026-06-06 09:00:34', 0),
(7, 'D-1007', '赵德胜', '158****6789', '3301**********6789', 'A2', '2028-06-30', 7, '/uploads/seed/avatar/02.jpg', 1, '2026-06-09 09:00:14', 0),
(8, 'D-1008', '孙建平', '159****0123', '3301**********0123', 'B2', '2027-04-16', 8, '/uploads/seed/avatar/03.jpg', 1, '2026-06-12 09:00:13', 0);

INSERT INTO sys_user (id, username, password, real_name, avatar, phone, email, org_id, role_id, point_id, driver_id, status, login_fail, lock_until, last_login, create_time, update_time, deleted) VALUES
(NULL, 'admin', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '周建明', '/uploads/seed/avatar/01.jpg', '13700001379', 'admin@waste.gov.cn', 5, 1, NULL, NULL, 1, 0, NULL, '2026-10-28 08:20:32', '2026-05-08 09:00:36', '2026-10-28 08:20:16', 0),
(NULL, 'dispatcher01', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '李振华', '/uploads/seed/avatar/02.jpg', '13700002758', 'dispatcher01@waste.gov.cn', 4, 2, NULL, NULL, 1, 0, NULL, '2026-10-28 08:20:22', '2026-05-10 09:00:53', '2026-10-28 08:20:18', 0),
(NULL, 'dispatcher02', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '何晓雯', '/uploads/seed/avatar/03.jpg', '13700004137', 'dispatcher02@waste.gov.cn', 5, 2, NULL, NULL, 1, 0, NULL, '2026-10-28 08:20:31', '2026-05-12 09:00:26', '2026-10-28 08:20:54', 0),
(NULL, 'point01', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '王秀兰', '/uploads/seed/avatar/04.jpg', '13700005516', 'point01@waste.gov.cn', 6, 3, 2, NULL, 2, 0, NULL, '2026-10-28 08:20:58', '2026-05-14 09:00:35', '2026-10-28 08:20:14', 0),
(NULL, 'point02', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '李国庆', '/uploads/seed/avatar/05.jpg', '13700006895', 'point02@waste.gov.cn', 3, 3, 1, NULL, 1, 0, NULL, '2026-10-28 08:20:17', '2026-05-16 09:00:29', '2026-10-28 08:20:16', 0),
(NULL, 'point03', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '刘敏', '/uploads/seed/avatar/06.jpg', '13700008274', 'point03@waste.gov.cn', 2, 3, 5, NULL, 5, 0, NULL, '2026-10-28 08:20:14', '2026-05-18 09:00:24', '2026-10-28 08:20:26', 0),
(NULL, 'driver01', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '陈伟强', '/uploads/seed/avatar/07.jpg', '13700009653', 'driver01@waste.gov.cn', 1, 4, NULL, 1, 1, 0, NULL, '2026-10-28 08:20:59', '2026-05-20 09:00:32', '2026-10-28 08:20:51', 0),
(NULL, 'driver02', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '黄志明', '/uploads/seed/avatar/08.jpg', '13700011032', 'driver02@waste.gov.cn', 2, 4, NULL, 2, 2, 0, NULL, '2026-10-28 08:20:18', '2026-05-22 09:00:35', '2026-10-28 08:20:08', 0),
(NULL, 'driver03', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '王建军', '/uploads/seed/avatar/09.jpg', '13700012411', 'driver03@waste.gov.cn', 3, 4, NULL, 3, 3, 0, NULL, '2026-10-28 08:20:59', '2026-05-24 09:00:53', '2026-10-28 08:20:18', 0),
(NULL, 'driver04', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '刘海涛', '/uploads/seed/avatar/10.jpg', '13700013790', 'driver04@waste.gov.cn', 2, 4, NULL, 4, 4, 0, NULL, '2026-10-28 08:20:30', '2026-05-26 09:00:39', '2026-10-28 08:20:12', 0),
(NULL, 'driver05', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '李国强', '/uploads/seed/avatar/11.jpg', '13700015169', 'driver05@waste.gov.cn', 1, 4, NULL, 5, 1, 0, NULL, '2026-10-28 08:20:15', '2026-05-28 09:00:21', '2026-10-28 08:20:45', 0),
(NULL, 'ops02', '$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK', '孙志刚', '/uploads/seed/avatar/12.jpg', '13700016548', 'ops02@waste.gov.cn', 5, 1, NULL, NULL, 3, 0, NULL, '2026-10-28 08:20:44', '2026-05-30 09:00:18', '2026-10-28 08:20:29', 0);

INSERT INTO sys_dict (id, dict_type, dict_label, dict_value, sort, status) VALUES
(1, 'waste_type', '生活垃圾', '生活垃圾', 1, 1),
(2, 'waste_type', '建筑垃圾', '建筑垃圾', 2, 1),
(3, 'waste_type', '餐厨垃圾', '餐厨垃圾', 3, 1),
(4, 'waste_type', '大件垃圾', '大件垃圾', 4, 1),
(5, 'waste_type', '园林绿化', '园林绿化', 5, 1),
(6, 'point_status', '正常', 'NORMAL', 1, 1),
(7, 'point_status', '满溢', 'OVERFLOW', 2, 1),
(8, 'point_status', '停用', 'DISABLED', 3, 1),
(9, 'order_status', '待派车', 'PENDING_DISPATCH', 1, 1),
(10, 'order_status', '已接单', 'ACCEPTED', 2, 1),
(11, 'order_status', '清运中', 'RUNNING', 3, 1),
(12, 'order_status', '待确认', 'PENDING_CONFIRM', 4, 1),
(13, 'order_status', '已完成', 'DONE', 5, 1),
(14, 'order_status', '已取消', 'CANCELED', 6, 1),
(15, 'order_status', '异常', 'ABNORMAL', 7, 1),
(16, 'overflow_level', '轻微', 'LIGHT', 1, 1),
(17, 'overflow_level', '明显', 'OBVIOUS', 2, 1),
(18, 'overflow_level', '严重', 'SERIOUS', 3, 1),
(19, 'exception_type', '车辆故障', 'VEHICLE_FAULT', 1, 1),
(20, 'exception_type', '收集点无法进入', 'UNREACHABLE', 2, 1),
(21, 'exception_type', '重量超载', 'OVERLOAD', 3, 1),
(22, 'exception_type', '漏站', 'MISS_STOP', 4, 1),
(23, 'exception_type', '其他', 'OTHER', 5, 1),
(24, 'dispose_type', '填埋', 'LAND_FILL', 1, 1),
(25, 'dispose_type', '焚烧发电', 'INCINERATE', 2, 1),
(26, 'dispose_type', '资源化利用', 'RECYCLE', 3, 1),
(27, 'frequency', '每日', 'DAILY', 1, 1),
(28, 'frequency', '隔日', 'EVERY_2_DAYS', 2, 1),
(29, 'frequency', '每周', 'WEEKLY', 3, 1),
(30, 'order_type', '周期计划', 'PLAN', 1, 1),
(31, 'order_type', '紧急插单', 'URGENT', 2, 1),
(32, 'order_type', '合并任务', 'MERGE', 3, 1);

INSERT INTO collection_plan (id, plan_code, point_id, route_id, waste_type, frequency, weekday, estimated_weight, next_date, status, create_time, deleted) VALUES
(1, 'PL-2026-001', 8, 2, '餐厨垃圾', 'EVERY_2_DAYS', NULL, 7.35, '2026-11-06', 'ON', '2026-05-26 10:00:28', 0),
(2, 'PL-2026-002', 15, 3, '园林绿化', 'WEEKLY', 1, 3.51, '2026-11-03', 'ON', '2026-05-28 10:00:00', 0),
(3, 'PL-2026-003', 2, 2, '生活垃圾', 'WEEKLY', 4, 5.68, '2026-11-01', 'ON', '2026-05-30 10:00:39', 0),
(4, 'PL-2026-004', 9, 3, '建筑垃圾', 'DAILY', NULL, 2.88, '2026-11-04', 'ON', '2026-06-01 10:00:02', 0),
(5, 'PL-2026-005', 16, 4, '建筑垃圾', 'EVERY_2_DAYS', NULL, 4.54, '2026-11-06', 'ON', '2026-06-03 10:00:46', 0),
(6, 'PL-2026-006', 3, 3, '餐厨垃圾', 'WEEKLY', 1, 3.32, '2026-11-02', 'ON', '2026-06-05 10:00:53', 0),
(7, 'PL-2026-007', 10, 4, '餐厨垃圾', 'WEEKLY', 4, 4.34, '2026-11-05', 'ON', '2026-06-07 10:00:44', 0),
(8, 'PL-2026-008', 17, 5, '餐厨垃圾', 'DAILY', NULL, 4.45, '2026-11-04', 'ON', '2026-06-09 10:00:23', 0),
(9, 'PL-2026-009', 4, 4, '生活垃圾', 'EVERY_2_DAYS', NULL, 10.83, '2026-11-06', 'ON', '2026-06-11 10:00:10', 0),
(10, 'PL-2026-010', 11, 5, '大件垃圾', 'WEEKLY', 1, 3.02, '2026-11-04', 'ON', '2026-06-13 10:00:18', 0),
(11, 'PL-2026-011', 18, 6, '大件垃圾', 'WEEKLY', 4, 3.37, '2026-10-31', 'ON', '2026-06-15 10:00:03', 0),
(12, 'PL-2026-012', 5, 5, '园林绿化', 'DAILY', NULL, 3.06, '2026-11-06', 'ON', '2026-06-17 10:00:49', 0),
(13, 'PL-2026-013', 12, 6, '园林绿化', 'EVERY_2_DAYS', NULL, 2.43, '2026-11-01', 'ON', '2026-06-19 10:00:43', 0),
(14, 'PL-2026-014', 19, 1, '大件垃圾', 'WEEKLY', 1, 11.19, '2026-11-04', 'ON', '2026-06-21 10:00:34', 0),
(15, 'PL-2026-015', 6, 6, '餐厨垃圾', 'WEEKLY', 4, 2.84, '2026-11-01', 'ON', '2026-06-23 10:00:17', 0),
(16, 'PL-2026-016', 13, 1, '园林绿化', 'DAILY', NULL, 5.54, '2026-10-31', 'ON', '2026-06-25 10:00:03', 0),
(17, 'PL-2026-017', 20, 2, '餐厨垃圾', 'EVERY_2_DAYS', NULL, 4.19, '2026-11-01', 'ON', '2026-06-27 10:00:03', 0),
(18, 'PL-2026-018', 7, 1, '大件垃圾', 'WEEKLY', 1, 4.32, '2026-11-01', 'ON', '2026-06-29 10:00:08', 0),
(19, 'PL-2026-019', 14, 2, '餐厨垃圾', 'WEEKLY', 4, 8.93, '2026-11-05', 'ON', '2026-07-01 10:00:33', 0),
(20, 'PL-2026-020', 1, 1, '园林绿化', 'DAILY', NULL, 6.33, '2026-11-01', 'ON', '2026-07-03 10:00:19', 0),
(21, 'PL-2026-021', 8, 2, '生活垃圾', 'EVERY_2_DAYS', NULL, 6.38, '2026-11-02', 'ON', '2026-07-05 10:00:17', 0),
(22, 'PL-2026-022', 15, 3, '生活垃圾', 'WEEKLY', 1, 4.21, '2026-11-02', 'ON', '2026-07-07 10:00:28', 0),
(23, 'PL-2026-023', 2, 2, '园林绿化', 'WEEKLY', 4, 4.59, '2026-11-03', 'ON', '2026-07-09 10:00:37', 0),
(24, 'PL-2026-024', 9, 3, '生活垃圾', 'DAILY', NULL, 3.24, '2026-11-02', 'ON', '2026-07-11 10:00:14', 0);

INSERT INTO complaint (id, point_id, content, level, source, handle_status, happen_time, create_time) VALUES
(1, 6, '垃圾散落未清扫', 'MID', '热线', 'DONE', '2026-07-20 11:17:59', '2026-07-20 11:17:59'),
(2, 11, '垃圾满溢异味较大', 'HIGH', '微信', 'DONE', '2026-08-03 11:10:06', '2026-08-03 11:10:06'),
(3, 16, '垃圾满溢异味较大', 'HIGH', '微信', 'DONE', '2026-06-23 18:54:54', '2026-06-23 18:54:54'),
(4, 1, '垃圾散落未清扫', 'MID', '微信', 'DONE', '2026-06-07 20:04:45', '2026-06-07 20:04:45'),
(5, 6, '垃圾满溢异味较大', 'MID', '微信', 'PENDING', '2026-09-28 14:10:56', '2026-09-28 14:10:56'),
(6, 11, '夜间清运噪音扰民', 'LOW', '微信', 'DONE', '2026-10-23 19:31:56', '2026-10-23 19:31:56'),
(7, 16, '清运不及时影响出行', 'LOW', '热线', 'PENDING', '2026-08-02 08:41:48', '2026-08-02 08:41:48'),
(8, 1, '清运不及时影响出行', 'LOW', '热线', 'DONE', '2026-10-25 11:36:42', '2026-10-25 11:36:42'),
(9, 6, '垃圾散落未清扫', 'HIGH', '微信', 'PENDING', '2026-10-05 19:09:28', '2026-10-05 19:09:28'),
(10, 11, '垃圾满溢异味较大', 'HIGH', '热线', 'PENDING', '2026-10-04 17:37:54', '2026-10-04 17:37:54'),
(11, 16, '夜间清运噪音扰民', 'HIGH', '微信', 'DONE', '2026-06-17 17:01:46', '2026-06-17 17:01:46'),
(12, 1, '垃圾满溢异味较大', 'HIGH', '热线', 'DONE', '2026-07-29 12:28:26', '2026-07-29 12:28:26'),
(13, 6, '垃圾散落未清扫', 'LOW', '现场', 'DONE', '2026-09-07 10:13:21', '2026-09-07 10:13:21'),
(14, 11, '收集点周边蚊虫较多', 'LOW', '微信', 'PENDING', '2026-06-27 18:02:40', '2026-06-27 18:02:40'),
(15, 16, '夜间清运噪音扰民', 'HIGH', '热线', 'PENDING', '2026-10-18 20:30:19', '2026-10-18 20:30:19'),
(16, 1, '清运不及时影响出行', 'HIGH', '热线', 'DONE', '2026-08-29 09:18:08', '2026-08-29 09:18:08'),
(17, 6, '清运不及时影响出行', 'LOW', '现场', 'DONE', '2026-07-05 08:32:29', '2026-07-05 08:32:29'),
(18, 11, '垃圾满溢异味较大', 'LOW', '热线', 'DONE', '2026-09-19 19:10:54', '2026-09-19 19:10:54'),
(19, 16, '垃圾散落未清扫', 'MID', '现场', 'DONE', '2026-08-30 18:28:04', '2026-08-30 18:28:04'),
(20, 1, '垃圾满溢异味较大', 'HIGH', '现场', 'PENDING', '2026-07-27 14:17:26', '2026-07-27 14:17:26');

INSERT INTO dispatch_order (id, order_no, order_type, route_id, vehicle_id, driver_id, dispose_site_id, point_summary, stop_count, plan_time, dispatch_time, estimated_weight, actual_weight, status, priority_score, priority_grade, dispatcher_id, reason, create_by, create_time, update_time, version, deleted) VALUES
(1, 'QD20260917-0001', 'PLAN', 2, 4, 6, 3, '滨江花园西区站', 1, '2026-09-17 15:00:28', '2026-09-17 01:00:28', 7.12, NULL, 'PENDING_DISPATCH', 58.6, 'P3', 2, NULL, 11, '2026-09-16 13:00:28', '2026-09-17 23:00:28', 1, 0),
(2, 'QD20260918-0002', 'PLAN', 3, 7, 3, 5, '高新产品园 A 区站', 1, '2026-09-18 09:45:30', '2026-09-17 21:45:30', 2.9, NULL, 'ACCEPTED', 53.9, 'P3', 2, NULL, 11, '2026-09-17 20:45:30', '2026-09-18 16:45:30', 0, 0),
(3, 'QD20260919-0003', 'PLAN', 2, 1, 8, 2, '锦绣花园小区北门站', 1, '2026-09-19 09:30:56', '2026-09-18 22:30:56', 4.24, NULL, 'RUNNING', 74.6, 'P2', 2, NULL, 11, '2026-09-18 16:30:56', '2026-09-19 11:30:56', 0, 0),
(4, 'QD20260920-0004', 'PLAN', 3, 4, 5, 4, '城南小学北门站', 1, '2026-09-20 07:00:18', '2026-09-19 21:00:18', 3.57, 3.19, 'PENDING_CONFIRM', 83.6, 'P2', 2, NULL, 11, '2026-09-19 09:00:18', '2026-09-20 14:00:18', 1, 0),
(5, 'QD20260921-0005', 'MERGE', 4, 7, 2, 1, '高新宿舍区站、滨江公园东门站、滨江路建材市场站', 3, '2026-09-21 14:30:05', '2026-09-21 06:30:05', 16.78, 18.46, 'DONE', 74.1, 'P2', 2, NULL, 11, '2026-09-20 19:30:05', '2026-09-21 15:30:05', 0, 0),
(6, 'QD20260922-0006', 'PLAN', 3, 1, 7, 3, '第三小学后街站', 1, '2026-09-22 10:30:21', '2026-09-21 16:30:21', 3.04, 3.31, 'DONE', 67.4, 'P2', 2, NULL, 11, '2026-09-21 18:30:21', '2026-09-22 15:30:21', 1, 0),
(7, 'QD20260923-0007', 'URGENT', 4, 4, 4, 5, '锦绣花园东门站', 1, '2026-09-23 11:15:34', '2026-09-23 02:15:34', 4.61, 4.23, 'DONE', 82.3, 'P2', 2, NULL, 11, '2026-09-22 13:15:34', '2026-09-23 19:15:34', 2, 0),
(8, 'QD20260924-0008', 'PLAN', 5, 7, 1, 2, '城北农贸集市站', 1, '2026-09-24 14:30:43', '2026-09-24 06:30:43', 4.37, NULL, 'CANCELED', 88.2, 'P1', 2, '收集点临时封闭施工，当日无法进场作业', 11, '2026-09-23 14:30:43', '2026-09-24 17:30:43', 1, 0),
(9, 'QD20260925-0009', 'PLAN', 4, 1, 6, 4, '滨江路建材市场站', 1, '2026-09-25 14:15:24', '2026-09-25 05:15:24', 5.53, 5.81, 'ABNORMAL', 70.8, 'P2', 2, '车辆途中故障，已建立异常并改派', 11, '2026-09-24 12:15:24', '2026-09-25 19:15:24', 1, 0),
(10, 'QD20260926-0010', 'MERGE', 5, 4, 3, 1, '老城菜市场西站、高新产品园 A 区站、城南工业园站', 3, '2026-09-26 11:45:03', '2026-09-25 16:45:03', 18.13, NULL, 'PENDING_DISPATCH', 55.7, 'P3', 2, NULL, 11, '2026-09-25 18:45:03', '2026-09-26 19:45:03', 1, 0),
(11, 'QD20260927-0011', 'PLAN', 6, 7, 8, 3, '城北中学站', 1, '2026-09-27 11:15:34', '2026-09-26 18:15:34', 3.16, NULL, 'ACCEPTED', 46.4, 'P3', 2, NULL, 11, '2026-09-26 19:15:34', '2026-09-27 18:15:34', 1, 0),
(12, 'QD20260928-0012', 'PLAN', 5, 1, 5, 5, '高新科技园 B 区站', 1, '2026-09-28 09:30:51', '2026-09-27 19:30:51', 3.78, NULL, 'RUNNING', 52.5, 'P3', 2, NULL, 11, '2026-09-27 17:30:51', '2026-09-28 17:30:51', 2, 0),
(13, 'QD20260929-0013', 'PLAN', 6, 4, 2, 2, '老城医院后门站', 1, '2026-09-29 11:15:16', '2026-09-28 20:15:16', 2.92, 2.74, 'PENDING_CONFIRM', 83.3, 'P2', 2, NULL, 11, '2026-09-28 09:15:16', '2026-09-29 14:15:16', 2, 0),
(14, 'QD20260930-0014', 'URGENT', 1, 7, 7, 4, '城南工业园站', 1, '2026-09-30 06:15:35', '2026-09-29 14:15:35', 12.04, 12.23, 'DONE', 49.7, 'P3', 2, NULL, 11, '2026-09-29 04:15:35', '2026-09-30 10:15:35', 0, 0),
(15, 'QD20261001-0015', 'MERGE', 6, 1, 4, 1, '城北乡镇卫生院站、锦绣花园东门站、滨江装饰城站', 3, '2026-10-01 09:15:44', '2026-09-30 21:15:44', 13.55, 12.73, 'DONE', 87.3, 'P1', 2, NULL, 11, '2026-09-30 17:15:44', '2026-10-01 11:15:44', 0, 0),
(16, 'QD20261002-0016', 'PLAN', 1, 4, 1, 3, '滨江写字楼群站', 1, '2026-10-02 13:15:20', '2026-10-01 23:15:20', 3.6, 3.88, 'DONE', 60.5, 'P3', 2, NULL, 11, '2026-10-01 12:15:20', '2026-10-02 22:15:20', 1, 0),
(17, 'QD20261003-0017', 'PLAN', 2, 7, 6, 5, '滨江公园东门站', 1, '2026-10-03 07:45:55', '2026-10-02 15:45:55', 3.22, NULL, 'CANCELED', 59.3, 'P3', 2, '收集点临时封闭施工，当日无法进场作业', 11, '2026-10-02 08:45:55', '2026-10-03 15:45:55', 1, 0),
(18, 'QD20261004-0018', 'PLAN', 1, 1, 3, 2, '老城文化广场站', 1, '2026-10-04 09:00:07', '2026-10-03 23:00:07', 3.94, 3.99, 'ABNORMAL', 70.5, 'P2', 2, '车辆途中故障，已建立异常并改派', 11, '2026-10-03 15:00:07', '2026-10-04 13:00:07', 0, 0),
(19, 'QD20261005-0019', 'PLAN', 2, 4, 8, 4, '滨江装饰城站', 1, '2026-10-05 15:45:37', '2026-10-05 03:45:37', 6.26, NULL, 'PENDING_DISPATCH', 56.9, 'P3', 2, NULL, 11, '2026-10-04 21:45:37', '2026-10-05 21:45:37', 2, 0),
(20, 'QD20261006-0020', 'MERGE', 1, 7, 5, 1, '城南农贸市场东门站、高新科技园 B 区站、城南小学北门站', 3, '2026-10-06 13:45:18', '2026-10-06 04:45:18', 11.82, NULL, 'ACCEPTED', 69.3, 'P2', 2, NULL, 11, '2026-10-05 22:45:18', '2026-10-06 17:45:18', 1, 0),
(21, 'QD20261007-0021', 'URGENT', 2, 1, 2, 3, '滨江花园西区站', 1, '2026-10-07 14:15:31', '2026-10-06 21:15:31', 4.24, NULL, 'RUNNING', 78.3, 'P2', 2, NULL, 11, '2026-10-06 16:15:31', '2026-10-07 23:15:31', 0, 0),
(22, 'QD20261008-0022', 'PLAN', 3, 4, 7, 5, '高新产品园 A 区站', 1, '2026-10-08 12:15:15', '2026-10-07 22:15:15', 3.41, 3.72, 'PENDING_CONFIRM', 60.9, 'P3', 2, NULL, 11, '2026-10-08 00:15:15', '2026-10-08 17:15:15', 1, 0),
(23, 'QD20261009-0023', 'PLAN', 2, 7, 4, 2, '锦绣花园小区北门站', 1, '2026-10-09 09:30:57', '2026-10-08 22:30:57', 5.03, 4.85, 'DONE', 90.8, 'P1', 2, NULL, 11, '2026-10-08 07:30:57', '2026-10-09 17:30:57', 2, 0),
(24, 'QD20261010-0024', 'PLAN', 3, 1, 1, 4, '城南小学北门站', 1, '2026-10-10 14:15:26', '2026-10-09 22:15:26', 2.98, 2.6, 'DONE', 74.1, 'P2', 2, NULL, 11, '2026-10-09 14:15:26', '2026-10-10 15:15:26', 0, 0),
(25, 'QD20261011-0025', 'MERGE', 4, 4, 6, 1, '高新宿舍区站、滨江公园东门站、滨江路建材市场站', 3, '2026-10-11 08:15:24', '2026-10-10 14:15:24', 15.84, 15.61, 'DONE', 65.8, 'P2', 2, NULL, 11, '2026-10-10 11:15:24', '2026-10-11 15:15:24', 0, 0),
(26, 'QD20261012-0026', 'PLAN', 3, 7, 3, 3, '第三小学后街站', 1, '2026-10-12 10:45:33', '2026-10-11 17:45:33', 3.41, NULL, 'CANCELED', 82.3, 'P2', 2, '收集点临时封闭施工，当日无法进场作业', 11, '2026-10-11 08:45:33', '2026-10-12 16:45:33', 2, 0),
(27, 'QD20261013-0027', 'PLAN', 4, 1, 8, 5, '锦绣花园东门站', 1, '2026-10-13 11:00:42', '2026-10-12 23:00:42', 3.58, 3.3, 'ABNORMAL', 87.2, 'P1', 2, '车辆途中故障，已建立异常并改派', 11, '2026-10-12 16:00:42', '2026-10-13 18:00:42', 0, 0),
(28, 'QD20261014-0028', 'URGENT', 5, 4, 5, 2, '城北农贸集市站', 1, '2026-10-14 13:30:49', '2026-10-14 03:30:49', 3.07, NULL, 'PENDING_DISPATCH', 47.6, 'P3', 2, NULL, 11, '2026-10-13 17:30:49', '2026-10-14 17:30:49', 1, 0),
(29, 'QD20261015-0029', 'PLAN', 4, 7, 2, 4, '滨江路建材市场站', 1, '2026-10-15 15:45:30', '2026-10-15 06:45:30', 6.86, NULL, 'ACCEPTED', 69.7, 'P2', 2, NULL, 11, '2026-10-14 18:45:30', '2026-10-15 19:45:30', 0, 0),
(30, 'QD20261016-0030', 'MERGE', 5, 1, 7, 1, '老城菜市场西站、高新产品园 A 区站、城南工业园站', 3, '2026-10-16 10:30:09', '2026-10-15 15:30:09', 16.21, NULL, 'RUNNING', 66.3, 'P2', 2, NULL, 11, '2026-10-15 19:30:09', '2026-10-16 19:30:09', 0, 0),
(31, 'QD20261017-0031', 'PLAN', 6, 4, 4, 3, '城北中学站', 1, '2026-10-17 14:30:08', '2026-10-17 01:30:08', 3.06, 3.0, 'PENDING_CONFIRM', 48.3, 'P3', 2, NULL, 11, '2026-10-17 00:30:08', '2026-10-17 21:30:08', 1, 0),
(32, 'QD20261018-0032', 'PLAN', 5, 7, 1, 5, '高新科技园 B 区站', 1, '2026-10-18 15:30:34', '2026-10-18 04:30:34', 3.24, 3.55, 'DONE', 72.8, 'P2', 2, NULL, 11, '2026-10-17 20:30:34', '2026-10-18 17:30:34', 1, 0),
(33, 'QD20261019-0033', 'PLAN', 6, 1, 6, 2, '老城医院后门站', 1, '2026-10-19 13:45:40', '2026-10-19 05:45:40', 2.92, 3.13, 'DONE', 78.4, 'P2', 2, NULL, 11, '2026-10-18 17:45:40', '2026-10-19 18:45:40', 0, 0),
(34, 'QD20261020-0034', 'PLAN', 1, 4, 3, 4, '城南工业园站', 1, '2026-10-20 11:00:27', '2026-10-19 17:00:27', 8.33, 7.62, 'DONE', 88.6, 'P1', 2, NULL, 11, '2026-10-19 20:00:27', '2026-10-20 15:00:27', 1, 0);

INSERT INTO route_stop (id, order_id, point_id, seq, plan_arrive, arrive_time, leave_time, estimated_weight, actual_weight, site_image, status, remark) VALUES
(1, 1, 8, 1, '2026-09-17 15:00:28', NULL, NULL, 7.12, NULL, NULL, 'WAITING', NULL),
(2, 2, 15, 1, '2026-09-18 09:45:30', NULL, NULL, 2.9, NULL, NULL, 'WAITING', NULL),
(3, 3, 2, 1, '2026-09-19 09:30:56', '2026-09-19 09:30:56', '2026-09-19 10:01:56', 4.24, 1.7, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(4, 4, 9, 1, '2026-09-20 07:00:18', '2026-09-20 07:00:18', '2026-09-20 07:23:18', 3.57, 3.63, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(5, 5, 16, 1, '2026-09-21 14:30:05', '2026-09-21 14:30:05', '2026-09-21 14:53:05', 5.59, 5.41, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(6, 5, 20, 2, '2026-09-21 15:10:05', '2026-09-21 15:13:05', '2026-09-21 15:39:05', 5.59, 6.04, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(7, 5, 4, 3, '2026-09-21 15:50:05', '2026-09-21 15:54:05', '2026-09-21 16:23:05', 5.59, 5.51, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(8, 6, 3, 1, '2026-09-22 10:30:21', '2026-09-22 10:30:21', '2026-09-22 11:05:21', 3.04, 3.59, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(9, 7, 10, 1, '2026-09-23 11:15:34', '2026-09-23 11:15:34', '2026-09-23 12:00:34', 4.61, 4.68, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(10, 8, 17, 1, '2026-09-24 14:30:43', NULL, NULL, 4.37, NULL, NULL, 'SKIPPED', '收集点当日封闭'),
(11, 9, 4, 1, '2026-09-25 14:15:24', '2026-09-25 14:15:24', '2026-09-25 14:53:24', 5.53, 5.42, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(12, 10, 11, 1, '2026-09-26 11:45:03', NULL, NULL, 6.04, NULL, NULL, 'WAITING', NULL),
(13, 10, 15, 2, '2026-09-26 12:25:03', NULL, NULL, 6.04, NULL, NULL, 'WAITING', NULL),
(14, 10, 19, 3, '2026-09-26 13:05:03', NULL, NULL, 6.04, NULL, NULL, 'WAITING', NULL),
(15, 11, 18, 1, '2026-09-27 11:15:34', NULL, NULL, 3.16, NULL, NULL, 'WAITING', NULL),
(16, 12, 5, 1, '2026-09-28 09:30:51', '2026-09-28 09:30:51', '2026-09-28 10:00:51', 3.78, 1.51, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(17, 13, 12, 1, '2026-09-29 11:15:16', '2026-09-29 11:15:16', '2026-09-29 11:37:16', 2.92, 3.04, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(18, 14, 19, 1, '2026-09-30 06:15:35', '2026-09-30 06:15:35', '2026-09-30 06:39:35', 12.04, 13.5, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(19, 15, 6, 1, '2026-10-01 09:15:44', '2026-10-01 09:15:44', '2026-10-01 09:43:44', 4.52, 4.27, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(20, 15, 10, 2, '2026-10-01 09:55:44', '2026-10-01 09:53:44', '2026-10-01 10:31:44', 4.52, 3.71, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(21, 15, 14, 3, '2026-10-01 10:35:44', '2026-10-01 10:45:44', '2026-10-01 11:23:44', 4.52, 4.85, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(22, 16, 13, 1, '2026-10-02 13:15:20', '2026-10-02 13:15:20', '2026-10-02 13:53:20', 3.6, 3.44, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(23, 17, 20, 1, '2026-10-03 07:45:55', NULL, NULL, 3.22, NULL, NULL, 'SKIPPED', '收集点当日封闭'),
(24, 18, 7, 1, '2026-10-04 09:00:07', '2026-10-04 09:00:07', '2026-10-04 09:45:07', 3.94, 4.24, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(25, 19, 14, 1, '2026-10-05 15:45:37', NULL, NULL, 6.26, NULL, NULL, 'WAITING', NULL),
(26, 20, 1, 1, '2026-10-06 13:45:18', NULL, NULL, 3.94, NULL, NULL, 'WAITING', NULL),
(27, 20, 5, 2, '2026-10-06 14:25:18', NULL, NULL, 3.94, NULL, NULL, 'WAITING', NULL),
(28, 20, 9, 3, '2026-10-06 15:05:18', NULL, NULL, 3.94, NULL, NULL, 'WAITING', NULL),
(29, 21, 8, 1, '2026-10-07 14:15:31', '2026-10-07 14:15:31', '2026-10-07 14:50:31', 4.24, 1.7, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(30, 22, 15, 1, '2026-10-08 12:15:15', '2026-10-08 12:15:15', '2026-10-08 12:44:15', 3.41, 4.14, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(31, 23, 2, 1, '2026-10-09 09:30:57', '2026-10-09 09:30:57', '2026-10-09 09:54:57', 5.03, 5.42, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(32, 24, 9, 1, '2026-10-10 14:15:26', '2026-10-10 14:15:26', '2026-10-10 14:44:26', 2.98, 2.59, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(33, 25, 16, 1, '2026-10-11 08:15:24', '2026-10-11 08:15:24', '2026-10-11 08:35:24', 5.28, 5.94, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(34, 25, 20, 2, '2026-10-11 08:55:24', '2026-10-11 08:53:24', '2026-10-11 09:33:24', 5.28, 4.54, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(35, 25, 4, 3, '2026-10-11 09:35:24', '2026-10-11 10:05:24', '2026-10-11 10:37:24', 5.28, 5.69, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(36, 26, 3, 1, '2026-10-12 10:45:33', NULL, NULL, 3.41, NULL, NULL, 'SKIPPED', '收集点当日封闭'),
(37, 27, 10, 1, '2026-10-13 11:00:42', '2026-10-13 11:00:42', '2026-10-13 11:36:42', 3.58, 3.59, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(38, 28, 17, 1, '2026-10-14 13:30:49', NULL, NULL, 3.07, NULL, NULL, 'WAITING', NULL),
(39, 29, 4, 1, '2026-10-15 15:45:30', NULL, NULL, 6.86, NULL, NULL, 'WAITING', NULL),
(40, 30, 11, 1, '2026-10-16 10:30:09', '2026-10-16 10:30:09', '2026-10-16 10:55:09', 5.4, 6.48, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(41, 30, 15, 2, '2026-10-16 11:10:09', '2026-10-16 11:30:09', NULL, 5.4, NULL, NULL, 'ARRIVED', NULL),
(42, 30, 19, 3, '2026-10-16 11:50:09', NULL, NULL, 5.4, NULL, NULL, 'WAITING', NULL),
(43, 31, 18, 1, '2026-10-17 14:30:08', '2026-10-17 14:30:08', '2026-10-17 15:02:08', 3.06, 2.88, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(44, 32, 5, 1, '2026-10-18 15:30:34', '2026-10-18 15:30:34', '2026-10-18 16:06:34', 3.24, 3.1, '/uploads/seed/site/02.jpg', 'DONE', NULL),
(45, 33, 12, 1, '2026-10-19 13:45:40', '2026-10-19 13:45:40', '2026-10-19 14:25:40', 2.92, 3.09, '/uploads/seed/site/01.jpg', 'DONE', NULL),
(46, 34, 19, 1, '2026-10-20 11:00:27', '2026-10-20 11:00:27', '2026-10-20 11:32:27', 8.33, 8.01, '/uploads/seed/site/02.jpg', 'DONE', NULL);

INSERT INTO weighing_record (id, record_no, order_id, dispose_site_id, in_weight, out_weight, net_weight, dispose_type, weighing_image, weigh_time, deviation, review_status, review_note, reviewer, create_time) VALUES
(1, 'WJ20260920-001', 4, 4, 6.6, 3.53, 3.07, 'INCINERATE', '/uploads/seed/weigh/01.jpg', '2026-09-20 10:00:18', 3.76, 'PASS', NULL, '孙志刚', '2026-09-20 15:00:18'),
(2, 'WJ20260921-002', 5, 1, 21.35, 3.15, 18.2, 'LAND_FILL', '/uploads/seed/weigh/02.jpg', '2026-09-21 17:30:05', 1.41, 'PASS', NULL, '孙志刚', '2026-09-21 21:30:05'),
(3, 'WJ20260922-003', 6, 3, 5.89, 2.6, 3.29, 'RECYCLE', '/uploads/seed/weigh/01.jpg', '2026-09-22 15:30:21', 0.6, 'PASS', NULL, '孙志刚', '2026-09-22 19:30:21'),
(4, 'WJ20260923-004', 7, 5, 8.34, 4.11, 4.23, 'RECYCLE', '/uploads/seed/weigh/02.jpg', '2026-09-23 17:15:34', 0.0, 'PASS', NULL, '孙志刚', '2026-09-23 19:15:34'),
(5, 'WJ20260925-005', 9, 4, 8.38, 2.5, 5.88, 'INCINERATE', '/uploads/seed/weigh/02.jpg', '2026-09-25 18:15:24', 1.2, 'PASS', NULL, '孙志刚', '2026-09-26 00:15:24'),
(6, 'WJ20260929-006', 13, 2, 6.29, 3.64, 2.65, 'INCINERATE', '/uploads/seed/weigh/02.jpg', '2026-09-29 14:15:16', 3.28, 'PASS', NULL, '孙志刚', '2026-09-29 21:15:16'),
(7, 'WJ20260930-007', 14, 4, 15.18, 3.29, 11.89, 'LAND_FILL', '/uploads/seed/weigh/01.jpg', '2026-09-30 11:15:35', 2.78, 'PASS', NULL, '孙志刚', '2026-09-30 15:15:35'),
(8, 'WJ20261001-008', 15, 1, 15.76, 3.61, 12.15, 'INCINERATE', '/uploads/seed/weigh/02.jpg', '2026-10-01 15:15:44', 4.56, 'PASS', NULL, '孙志刚', '2026-10-01 17:15:44'),
(9, 'WJ20261002-009', 16, 3, 6.68, 2.74, 3.94, 'LAND_FILL', '/uploads/seed/weigh/01.jpg', '2026-10-02 19:15:20', 1.55, 'PASS', NULL, '孙志刚', '2026-10-02 23:15:20'),
(10, 'WJ20261004-010', 18, 2, 7.31, 3.51, 3.8, 'RECYCLE', '/uploads/seed/weigh/01.jpg', '2026-10-04 15:00:07', 4.76, 'PASS', NULL, '孙志刚', '2026-10-04 17:00:07'),
(11, 'WJ20261008-011', 22, 5, 7.34, 3.57, 3.77, 'LAND_FILL', '/uploads/seed/weigh/01.jpg', '2026-10-08 15:15:15', 1.34, 'PASS', NULL, '孙志刚', '2026-10-08 21:15:15'),
(12, 'WJ20261009-012', 23, 2, 8.33, 3.54, 4.79, 'LAND_FILL', '/uploads/seed/weigh/02.jpg', '2026-10-09 13:30:57', 1.24, 'PASS', NULL, '孙志刚', '2026-10-09 17:30:57'),
(13, 'WJ20261010-013', 24, 4, 6.4, 3.79, 2.61, 'RECYCLE', '/uploads/seed/weigh/01.jpg', '2026-10-10 19:15:26', 0.38, 'PASS', NULL, '孙志刚', '2026-10-11 00:15:26'),
(14, 'WJ20261011-014', 25, 1, 19.43, 3.52, 15.91, 'LAND_FILL', '/uploads/seed/weigh/02.jpg', '2026-10-11 12:15:24', 1.92, 'PASS', NULL, '孙志刚', '2026-10-11 17:15:24'),
(15, 'WJ20261013-015', 27, 5, 6.74, 3.41, 3.33, 'INCINERATE', '/uploads/seed/weigh/02.jpg', '2026-10-13 15:00:42', 0.91, 'PASS', NULL, '孙志刚', '2026-10-13 19:00:42'),
(16, 'WJ20261017-016', 31, 3, 6.48, 3.5, 2.98, 'INCINERATE', '/uploads/seed/weigh/02.jpg', '2026-10-17 19:30:08', 0.67, 'PASS', NULL, '孙志刚', '2026-10-18 00:30:08'),
(17, 'WJ20261018-017', 32, 5, 6.34, 2.81, 3.53, 'INCINERATE', '/uploads/seed/weigh/01.jpg', '2026-10-18 20:30:34', 0.56, 'PASS', NULL, '孙志刚', '2026-10-19 00:30:34'),
(18, 'WJ20261019-018', 33, 2, 6.52, 3.45, 3.07, 'LAND_FILL', '/uploads/seed/weigh/02.jpg', '2026-10-19 16:45:40', 1.92, 'PASS', NULL, '孙志刚', '2026-10-19 20:45:40'),
(19, 'WJ20261020-019', 34, 4, 10.9, 3.37, 7.53, 'RECYCLE', '/uploads/seed/weigh/01.jpg', '2026-10-20 16:00:27', 1.18, 'PASS', NULL, '孙志刚', '2026-10-20 21:00:27');

INSERT INTO flow_log (id, biz_type, biz_id, biz_no, from_status, to_status, action, reason, operator, create_time) VALUES
(1, 'DISPATCH', 1, 'QD20260917-0001', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-16 19:00:28'),
(2, 'DISPATCH', 2, 'QD20260918-0002', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-17 13:45:30'),
(3, 'DISPATCH', 2, 'QD20260918-0002', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-17 19:45:30'),
(4, 'DISPATCH', 3, 'QD20260919-0003', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-18 13:30:56'),
(5, 'DISPATCH', 3, 'QD20260919-0003', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-18 19:30:56'),
(6, 'DISPATCH', 3, 'QD20260919-0003', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '孙建平', '2026-09-19 07:30:56'),
(7, 'DISPATCH', 4, 'QD20260920-0004', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-19 11:00:18'),
(8, 'DISPATCH', 4, 'QD20260920-0004', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-19 17:00:18'),
(9, 'DISPATCH', 4, 'QD20260920-0004', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '李国强', '2026-09-20 05:00:18'),
(10, 'DISPATCH', 4, 'QD20260920-0004', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '李国强', '2026-09-20 09:00:18'),
(11, 'DISPATCH', 5, 'QD20260921-0005', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-20 18:30:05'),
(12, 'DISPATCH', 5, 'QD20260921-0005', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-21 00:30:05'),
(13, 'DISPATCH', 5, 'QD20260921-0005', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '黄志明', '2026-09-21 12:30:05'),
(14, 'DISPATCH', 5, 'QD20260921-0005', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '黄志明', '2026-09-21 16:30:05'),
(15, 'DISPATCH', 5, 'QD20260921-0005', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-09-21 20:30:05'),
(16, 'DISPATCH', 6, 'QD20260922-0006', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-21 14:30:21'),
(17, 'DISPATCH', 6, 'QD20260922-0006', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-21 20:30:21'),
(18, 'DISPATCH', 6, 'QD20260922-0006', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '赵德胜', '2026-09-22 08:30:21'),
(19, 'DISPATCH', 6, 'QD20260922-0006', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '赵德胜', '2026-09-22 12:30:21'),
(20, 'DISPATCH', 6, 'QD20260922-0006', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-09-22 16:30:21'),
(21, 'DISPATCH', 7, 'QD20260923-0007', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-22 15:15:34'),
(22, 'DISPATCH', 7, 'QD20260923-0007', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-22 21:15:34'),
(23, 'DISPATCH', 7, 'QD20260923-0007', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '刘海涛', '2026-09-23 09:15:34'),
(24, 'DISPATCH', 7, 'QD20260923-0007', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '刘海涛', '2026-09-23 13:15:34'),
(25, 'DISPATCH', 7, 'QD20260923-0007', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-09-23 17:15:34'),
(26, 'DISPATCH', 8, 'QD20260924-0008', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-23 18:30:43'),
(27, 'DISPATCH', 8, 'QD20260924-0008', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-24 00:30:43'),
(28, 'DISPATCH', 8, 'QD20260924-0008', 'PENDING_DISPATCH', 'CANCELED', '取消任务', '收集点临时封闭施工，当日无法进场作业', '李振华', '2026-09-24 08:30:43'),
(29, 'DISPATCH', 9, 'QD20260925-0009', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-24 18:15:24'),
(30, 'DISPATCH', 9, 'QD20260925-0009', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-25 00:15:24'),
(31, 'DISPATCH', 9, 'QD20260925-0009', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '徐立新', '2026-09-25 12:15:24'),
(32, 'DISPATCH', 9, 'QD20260925-0009', 'RUNNING', 'ABNORMAL', '车辆故障上报', NULL, '徐立新', '2026-09-25 15:15:24'),
(33, 'DISPATCH', 10, 'QD20260926-0010', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-25 15:45:03'),
(34, 'DISPATCH', 11, 'QD20260927-0011', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-26 15:15:34'),
(35, 'DISPATCH', 11, 'QD20260927-0011', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-26 21:15:34'),
(36, 'DISPATCH', 12, 'QD20260928-0012', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-27 13:30:51'),
(37, 'DISPATCH', 12, 'QD20260928-0012', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-27 19:30:51'),
(38, 'DISPATCH', 12, 'QD20260928-0012', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '李国强', '2026-09-28 07:30:51'),
(39, 'DISPATCH', 13, 'QD20260929-0013', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-28 15:15:16'),
(40, 'DISPATCH', 13, 'QD20260929-0013', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-28 21:15:16'),
(41, 'DISPATCH', 13, 'QD20260929-0013', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '黄志明', '2026-09-29 09:15:16'),
(42, 'DISPATCH', 13, 'QD20260929-0013', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '黄志明', '2026-09-29 13:15:16'),
(43, 'DISPATCH', 14, 'QD20260930-0014', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-29 10:15:35'),
(44, 'DISPATCH', 14, 'QD20260930-0014', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-29 16:15:35'),
(45, 'DISPATCH', 14, 'QD20260930-0014', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '赵德胜', '2026-09-30 04:15:35'),
(46, 'DISPATCH', 14, 'QD20260930-0014', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '赵德胜', '2026-09-30 08:15:35'),
(47, 'DISPATCH', 14, 'QD20260930-0014', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-09-30 12:15:35'),
(48, 'DISPATCH', 15, 'QD20261001-0015', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-09-30 13:15:44'),
(49, 'DISPATCH', 15, 'QD20261001-0015', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-09-30 19:15:44'),
(50, 'DISPATCH', 15, 'QD20261001-0015', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '刘海涛', '2026-10-01 07:15:44'),
(51, 'DISPATCH', 15, 'QD20261001-0015', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '刘海涛', '2026-10-01 11:15:44'),
(52, 'DISPATCH', 15, 'QD20261001-0015', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-01 15:15:44'),
(53, 'DISPATCH', 16, 'QD20261002-0016', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-01 17:15:20'),
(54, 'DISPATCH', 16, 'QD20261002-0016', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-01 23:15:20'),
(55, 'DISPATCH', 16, 'QD20261002-0016', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '陈伟强', '2026-10-02 11:15:20'),
(56, 'DISPATCH', 16, 'QD20261002-0016', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '陈伟强', '2026-10-02 15:15:20'),
(57, 'DISPATCH', 16, 'QD20261002-0016', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-02 19:15:20'),
(58, 'DISPATCH', 17, 'QD20261003-0017', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-02 11:45:55'),
(59, 'DISPATCH', 17, 'QD20261003-0017', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-02 17:45:55'),
(60, 'DISPATCH', 17, 'QD20261003-0017', 'PENDING_DISPATCH', 'CANCELED', '取消任务', '收集点临时封闭施工，当日无法进场作业', '李振华', '2026-10-03 01:45:55'),
(61, 'DISPATCH', 18, 'QD20261004-0018', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-03 13:00:07'),
(62, 'DISPATCH', 18, 'QD20261004-0018', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-03 19:00:07'),
(63, 'DISPATCH', 18, 'QD20261004-0018', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '王建军', '2026-10-04 07:00:07'),
(64, 'DISPATCH', 18, 'QD20261004-0018', 'RUNNING', 'ABNORMAL', '车辆故障上报', NULL, '王建军', '2026-10-04 10:00:07'),
(65, 'DISPATCH', 19, 'QD20261005-0019', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-04 19:45:37'),
(66, 'DISPATCH', 20, 'QD20261006-0020', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-05 17:45:18'),
(67, 'DISPATCH', 20, 'QD20261006-0020', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-05 23:45:18'),
(68, 'DISPATCH', 21, 'QD20261007-0021', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-06 18:15:31'),
(69, 'DISPATCH', 21, 'QD20261007-0021', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-07 00:15:31'),
(70, 'DISPATCH', 21, 'QD20261007-0021', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '黄志明', '2026-10-07 12:15:31'),
(71, 'DISPATCH', 22, 'QD20261008-0022', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-07 16:15:15'),
(72, 'DISPATCH', 22, 'QD20261008-0022', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-07 22:15:15'),
(73, 'DISPATCH', 22, 'QD20261008-0022', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '赵德胜', '2026-10-08 10:15:15'),
(74, 'DISPATCH', 22, 'QD20261008-0022', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '赵德胜', '2026-10-08 14:15:15'),
(75, 'DISPATCH', 23, 'QD20261009-0023', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-08 13:30:57'),
(76, 'DISPATCH', 23, 'QD20261009-0023', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-08 19:30:57'),
(77, 'DISPATCH', 23, 'QD20261009-0023', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '刘海涛', '2026-10-09 07:30:57'),
(78, 'DISPATCH', 23, 'QD20261009-0023', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '刘海涛', '2026-10-09 11:30:57'),
(79, 'DISPATCH', 23, 'QD20261009-0023', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-09 15:30:57'),
(80, 'DISPATCH', 24, 'QD20261010-0024', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-09 18:15:26'),
(81, 'DISPATCH', 24, 'QD20261010-0024', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-10 00:15:26'),
(82, 'DISPATCH', 24, 'QD20261010-0024', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '陈伟强', '2026-10-10 12:15:26'),
(83, 'DISPATCH', 24, 'QD20261010-0024', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '陈伟强', '2026-10-10 16:15:26'),
(84, 'DISPATCH', 24, 'QD20261010-0024', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-10 20:15:26'),
(85, 'DISPATCH', 25, 'QD20261011-0025', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-10 12:15:24'),
(86, 'DISPATCH', 25, 'QD20261011-0025', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-10 18:15:24'),
(87, 'DISPATCH', 25, 'QD20261011-0025', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '徐立新', '2026-10-11 06:15:24'),
(88, 'DISPATCH', 25, 'QD20261011-0025', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '徐立新', '2026-10-11 10:15:24'),
(89, 'DISPATCH', 25, 'QD20261011-0025', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-11 14:15:24'),
(90, 'DISPATCH', 26, 'QD20261012-0026', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-11 14:45:33'),
(91, 'DISPATCH', 26, 'QD20261012-0026', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-11 20:45:33'),
(92, 'DISPATCH', 26, 'QD20261012-0026', 'PENDING_DISPATCH', 'CANCELED', '取消任务', '收集点临时封闭施工，当日无法进场作业', '李振华', '2026-10-12 04:45:33'),
(93, 'DISPATCH', 27, 'QD20261013-0027', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-12 15:00:42'),
(94, 'DISPATCH', 27, 'QD20261013-0027', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-12 21:00:42'),
(95, 'DISPATCH', 27, 'QD20261013-0027', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '孙建平', '2026-10-13 09:00:42'),
(96, 'DISPATCH', 27, 'QD20261013-0027', 'RUNNING', 'ABNORMAL', '车辆故障上报', NULL, '孙建平', '2026-10-13 12:00:42'),
(97, 'DISPATCH', 28, 'QD20261014-0028', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-13 17:30:49'),
(98, 'DISPATCH', 29, 'QD20261015-0029', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-14 19:45:30'),
(99, 'DISPATCH', 29, 'QD20261015-0029', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-15 01:45:30'),
(100, 'DISPATCH', 30, 'QD20261016-0030', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-15 14:30:09'),
(101, 'DISPATCH', 30, 'QD20261016-0030', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-15 20:30:09'),
(102, 'DISPATCH', 30, 'QD20261016-0030', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '赵德胜', '2026-10-16 08:30:09'),
(103, 'DISPATCH', 31, 'QD20261017-0031', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-16 18:30:08'),
(104, 'DISPATCH', 31, 'QD20261017-0031', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-17 00:30:08'),
(105, 'DISPATCH', 31, 'QD20261017-0031', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '刘海涛', '2026-10-17 12:30:08'),
(106, 'DISPATCH', 31, 'QD20261017-0031', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '刘海涛', '2026-10-17 16:30:08'),
(107, 'DISPATCH', 32, 'QD20261018-0032', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-17 19:30:34'),
(108, 'DISPATCH', 32, 'QD20261018-0032', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-18 01:30:34'),
(109, 'DISPATCH', 32, 'QD20261018-0032', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '陈伟强', '2026-10-18 13:30:34'),
(110, 'DISPATCH', 32, 'QD20261018-0032', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '陈伟强', '2026-10-18 17:30:34'),
(111, 'DISPATCH', 32, 'QD20261018-0032', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-18 21:30:34'),
(112, 'DISPATCH', 33, 'QD20261019-0033', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-18 17:45:40'),
(113, 'DISPATCH', 33, 'QD20261019-0033', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-18 23:45:40'),
(114, 'DISPATCH', 33, 'QD20261019-0033', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '徐立新', '2026-10-19 11:45:40'),
(115, 'DISPATCH', 33, 'QD20261019-0033', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '徐立新', '2026-10-19 15:45:40'),
(116, 'DISPATCH', 33, 'QD20261019-0033', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-19 19:45:40'),
(117, 'DISPATCH', 34, 'QD20261020-0034', NULL, 'PENDING_DISPATCH', '创建任务', NULL, '何晓雯', '2026-10-19 15:00:27'),
(118, 'DISPATCH', 34, 'QD20261020-0034', 'PENDING_DISPATCH', 'ACCEPTED', '派车', NULL, '李振华', '2026-10-19 21:00:27'),
(119, 'DISPATCH', 34, 'QD20261020-0034', 'ACCEPTED', 'RUNNING', '司机接单', NULL, '王建军', '2026-10-20 09:00:27'),
(120, 'DISPATCH', 34, 'QD20261020-0034', 'RUNNING', 'PENDING_CONFIRM', '完成各点清运', NULL, '王建军', '2026-10-20 13:00:27'),
(121, 'DISPATCH', 34, 'QD20261020-0034', 'PENDING_CONFIRM', 'DONE', '确认交接', NULL, '王海燕', '2026-10-20 17:00:27');

INSERT INTO dispatch_score (id, order_id, rule_id, rule_version, snapshot, v_load, v_stay, v_complaint, v_capacity, v_distance, v_type_match, s_load, s_stay, s_complaint, s_capacity, s_distance, s_type_match, total_score, grade, factors, unmet, improve, adopted, manual_adjust, adjust_reason, create_time) VALUES
(1, 1, 3, 3, '{"loadRate":56.1,"stayHours":64.0,"complaints":2,"vehicleCapacity":5.0,"distanceKm":0.8,"typeMatch":1}', 56.1, 64.0, 2, 5.0, 0.8, 1, 14.6, 21.3, 6.4, 0, 9.5, 6, 57.8, 'P3', '满载度 56%、滞留 64 小时、投诉 2 次', '车辆剩余容量不足', '点位距上一站 0.8 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-16 23:00:28'),
(2, 2, 3, 3, '{"loadRate":86.4,"stayHours":22.6,"complaints":2,"vehicleCapacity":8.0,"distanceKm":1.6,"typeMatch":1}', 86.4, 22.6, 2, 8.0, 1.6, 1, 22.5, 7.5, 6.4, 11.5, 8.9, 6, 62.8, 'P3', '满载度 86%、滞留 23 小时、投诉 2 次', '无', '点位距上一站 1.6 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-17 17:45:30'),
(3, 3, 3, 3, '{"loadRate":88.6,"stayHours":36.2,"complaints":2,"vehicleCapacity":8.0,"distanceKm":5.2,"typeMatch":1}', 88.6, 36.2, 2, 8.0, 5.2, 1, 23.0, 12.1, 6.4, 8.5, 6.5, 6, 62.5, 'P3', '满载度 89%、滞留 36 小时、投诉 2 次', '无', '点位距上一站 5.2 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-18 17:30:56'),
(4, 4, 3, 3, '{"loadRate":68.3,"stayHours":18.0,"complaints":1,"vehicleCapacity":5.0,"distanceKm":9.0,"typeMatch":0}', 68.3, 18.0, 1, 5.0, 9.0, 0, 17.8, 6.0, 3.2, 5.1, 4.0, 0, 36.1, 'NONE', '满载度 68%、滞留 18 小时、投诉 1 次', '无', '点位距上一站 9.0 km，建议调整线路顺序减少空驶', 0, 1, '原定车辆年检到期，改派同载重车辆', '2026-09-19 15:00:18'),
(5, 5, 3, 3, '{"loadRate":78.6,"stayHours":68.4,"complaints":5,"vehicleCapacity":8.0,"distanceKm":4.1,"typeMatch":1}', 78.6, 68.4, 5, 8.0, 4.1, 1, 20.4, 22.8, 16.0, 0, 7.3, 6, 72.5, 'P2', '满载度 79%、滞留 68 小时、投诉 5 次', '车辆剩余容量不足', '点位距上一站 4.1 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-20 22:30:05'),
(6, 6, 3, 3, '{"loadRate":70.4,"stayHours":69.1,"complaints":4,"vehicleCapacity":8.0,"distanceKm":11.5,"typeMatch":1}', 70.4, 69.1, 4, 8.0, 11.5, 1, 18.3, 23.0, 12.8, 11.2, 2.3, 6, 73.6, 'P2', '满载度 70%、滞留 69 小时、投诉 4 次', '无', '点位距上一站 11.5 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-21 18:30:21'),
(7, 7, 3, 3, '{"loadRate":76.5,"stayHours":29.2,"complaints":0,"vehicleCapacity":5.0,"distanceKm":6.2,"typeMatch":1}', 76.5, 29.2, 0, 5.0, 6.2, 1, 19.9, 9.7, 0.0, 1.4, 5.9, 6, 42.9, 'NONE', '满载度 76%、滞留 29 小时、投诉 0 次', '无', '点位距上一站 6.2 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-22 19:15:34'),
(8, 8, 3, 3, '{"loadRate":57.6,"stayHours":47.7,"complaints":1,"vehicleCapacity":8.0,"distanceKm":7.7,"typeMatch":1}', 57.6, 47.7, 1, 8.0, 7.7, 1, 15.0, 15.9, 3.2, 8.2, 4.9, 6, 53.2, 'P3', '满载度 58%、滞留 48 小时、投诉 1 次', '无', '点位距上一站 7.7 km，建议调整线路顺序减少空驶', 0, 1, '原定车辆年检到期，改派同载重车辆', '2026-09-23 22:30:43'),
(9, 9, 3, 3, '{"loadRate":77.1,"stayHours":68.1,"complaints":3,"vehicleCapacity":8.0,"distanceKm":4.7,"typeMatch":0}', 77.1, 68.1, 3, 8.0, 4.7, 0, 20.0, 22.7, 9.6, 5.6, 6.9, 0, 64.8, 'P3', '满载度 77%、滞留 68 小时、投诉 3 次', '无', '点位距上一站 4.7 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-24 22:15:24'),
(10, 10, 3, 3, '{"loadRate":65.8,"stayHours":36.5,"complaints":2,"vehicleCapacity":5.0,"distanceKm":6.0,"typeMatch":1}', 65.8, 36.5, 2, 5.0, 6.0, 1, 17.1, 12.2, 6.4, 0, 6.0, 6, 47.7, 'P3', '满载度 66%、滞留 36 小时、投诉 2 次', '车辆剩余容量不足', '点位距上一站 6.0 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-25 19:45:03'),
(11, 11, 3, 3, '{"loadRate":47.5,"stayHours":31.1,"complaints":0,"vehicleCapacity":8.0,"distanceKm":2.1,"typeMatch":1}', 47.5, 31.1, 0, 8.0, 2.1, 1, 12.3, 10.4, 0.0, 10.9, 8.6, 6, 48.2, 'P3', '满载度 48%、滞留 31 小时、投诉 0 次', '无', '点位距上一站 2.1 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-26 19:15:34'),
(12, 12, 3, 3, '{"loadRate":56.3,"stayHours":36.5,"complaints":1,"vehicleCapacity":8.0,"distanceKm":5.9,"typeMatch":1}', 56.3, 36.5, 1, 8.0, 5.9, 1, 14.6, 12.2, 3.2, 9.5, 6.1, 6, 51.6, 'P3', '满载度 56%、滞留 36 小时、投诉 1 次', '无', '点位距上一站 5.9 km，建议调整线路顺序减少空驶', 0, 1, '原定车辆年检到期，改派同载重车辆', '2026-09-27 17:30:51'),
(13, 13, 3, 3, '{"loadRate":58.8,"stayHours":19.0,"complaints":2,"vehicleCapacity":5.0,"distanceKm":5.8,"typeMatch":1}', 58.8, 19.0, 2, 5.0, 5.8, 1, 15.3, 6.3, 6.4, 7.5, 6.1, 6, 47.6, 'P3', '满载度 59%、滞留 19 小时、投诉 2 次', '无', '点位距上一站 5.8 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-28 19:15:16'),
(14, 14, 3, 3, '{"loadRate":88.8,"stayHours":53.2,"complaints":0,"vehicleCapacity":8.0,"distanceKm":11.4,"typeMatch":1}', 88.8, 53.2, 0, 8.0, 11.4, 1, 23.1, 17.7, 0.0, 0, 2.4, 6, 49.2, 'P3', '满载度 89%、滞留 53 小时、投诉 0 次', '车辆剩余容量不足', '点位距上一站 11.4 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-29 14:15:35'),
(15, 15, 3, 3, '{"loadRate":76.7,"stayHours":53.1,"complaints":0,"vehicleCapacity":8.0,"distanceKm":10.5,"typeMatch":1}', 76.7, 53.1, 0, 8.0, 10.5, 1, 19.9, 17.7, 0.0, 0, 3.0, 6, 46.6, 'P3', '满载度 77%、滞留 53 小时、投诉 0 次', '车辆剩余容量不足', '点位距上一站 10.5 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-09-30 17:15:44'),
(16, 16, 3, 3, '{"loadRate":57.8,"stayHours":30.2,"complaints":1,"vehicleCapacity":5.0,"distanceKm":8.9,"typeMatch":1}', 57.8, 30.2, 1, 5.0, 8.9, 1, 15.0, 10.1, 3.2, 5.0, 4.1, 6, 43.4, 'NONE', '满载度 58%、滞留 30 小时、投诉 1 次', '无', '点位距上一站 8.9 km，建议调整线路顺序减少空驶', 0, 1, '原定车辆年检到期，改派同载重车辆', '2026-10-01 21:15:20'),
(17, 17, 3, 3, '{"loadRate":64.8,"stayHours":25.1,"complaints":0,"vehicleCapacity":8.0,"distanceKm":10.3,"typeMatch":1}', 64.8, 25.1, 0, 8.0, 10.3, 1, 16.8, 8.4, 0.0, 10.8, 3.1, 6, 45.1, 'P3', '满载度 65%、滞留 25 小时、投诉 0 次', '无', '点位距上一站 10.3 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-02 15:45:55'),
(18, 18, 3, 3, '{"loadRate":47.9,"stayHours":43.9,"complaints":3,"vehicleCapacity":8.0,"distanceKm":11.8,"typeMatch":0}', 47.9, 43.9, 3, 8.0, 11.8, 0, 12.5, 14.6, 9.6, 9.1, 2.1, 0, 47.9, 'P3', '满载度 48%、滞留 44 小时、投诉 3 次', '无', '点位距上一站 11.8 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-03 17:00:07'),
(19, 19, 3, 3, '{"loadRate":79.3,"stayHours":27.1,"complaints":0,"vehicleCapacity":5.0,"distanceKm":7.8,"typeMatch":1}', 79.3, 27.1, 0, 5.0, 7.8, 1, 20.6, 9.0, 0.0, 0, 4.8, 6, 40.4, 'NONE', '满载度 79%、滞留 27 小时、投诉 0 次', '车辆剩余容量不足', '点位距上一站 7.8 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-04 23:45:37'),
(20, 20, 3, 3, '{"loadRate":84.8,"stayHours":56.5,"complaints":1,"vehicleCapacity":8.0,"distanceKm":6.2,"typeMatch":0}', 84.8, 56.5, 1, 8.0, 6.2, 0, 22.0, 18.8, 3.2, 0, 5.9, 0, 49.9, 'P3', '满载度 85%、滞留 56 小时、投诉 1 次', '车辆剩余容量不足', '点位距上一站 6.2 km，建议调整线路顺序减少空驶', 0, 1, '原定车辆年检到期，改派同载重车辆', '2026-10-05 21:45:18'),
(21, 21, 3, 3, '{"loadRate":49.7,"stayHours":53.7,"complaints":5,"vehicleCapacity":8.0,"distanceKm":1.0,"typeMatch":1}', 49.7, 53.7, 5, 8.0, 1.0, 1, 12.9, 17.9, 16.0, 8.5, 9.3, 6, 70.6, 'P2', '满载度 50%、滞留 54 小时、投诉 5 次', '无', '点位距上一站 1.0 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-06 22:15:31'),
(22, 22, 3, 3, '{"loadRate":55.6,"stayHours":56.0,"complaints":0,"vehicleCapacity":5.0,"distanceKm":4.7,"typeMatch":1}', 55.6, 56.0, 0, 5.0, 4.7, 1, 14.5, 18.7, 0.0, 5.7, 6.9, 6, 51.8, 'P3', '满载度 56%、滞留 56 小时、投诉 0 次', '无', '点位距上一站 4.7 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-07 20:15:15'),
(23, 23, 3, 3, '{"loadRate":93.5,"stayHours":44.4,"complaints":3,"vehicleCapacity":8.0,"distanceKm":6.4,"typeMatch":1}', 93.5, 44.4, 3, 8.0, 6.4, 1, 24.3, 14.8, 9.6, 6.7, 5.7, 6, 67.1, 'P2', '满载度 94%、滞留 44 小时、投诉 3 次', '无', '点位距上一站 6.4 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-08 17:30:57'),
(24, 24, 3, 3, '{"loadRate":80.7,"stayHours":39.0,"complaints":3,"vehicleCapacity":8.0,"distanceKm":8.6,"typeMatch":1}', 80.7, 39.0, 3, 8.0, 8.6, 1, 21.0, 13.0, 9.6, 11.3, 4.3, 6, 65.2, 'P2', '满载度 81%、滞留 39 小时、投诉 3 次', '无', '点位距上一站 8.6 km，建议调整线路顺序减少空驶', 0, 1, '原定车辆年检到期，改派同载重车辆', '2026-10-09 22:15:26'),
(25, 25, 3, 3, '{"loadRate":66.0,"stayHours":11.1,"complaints":5,"vehicleCapacity":5.0,"distanceKm":7.6,"typeMatch":1}', 66.0, 11.1, 5, 5.0, 7.6, 1, 17.2, 3.7, 16.0, 0, 4.9, 6, 47.8, 'P3', '满载度 66%、滞留 11 小时、投诉 5 次', '车辆剩余容量不足', '点位距上一站 7.6 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-10 16:15:24'),
(26, 26, 3, 3, '{"loadRate":66.7,"stayHours":13.5,"complaints":1,"vehicleCapacity":8.0,"distanceKm":1.5,"typeMatch":1}', 66.7, 13.5, 1, 8.0, 1.5, 1, 17.3, 4.5, 3.2, 10.3, 9.0, 6, 50.3, 'P3', '满载度 67%、滞留 14 小时、投诉 1 次', '无', '点位距上一站 1.5 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-11 18:45:33'),
(27, 27, 3, 3, '{"loadRate":70.2,"stayHours":41.7,"complaints":1,"vehicleCapacity":8.0,"distanceKm":9.2,"typeMatch":1}', 70.2, 41.7, 1, 8.0, 9.2, 1, 18.3, 13.9, 3.2, 9.9, 3.9, 6, 55.2, 'P3', '满载度 70%、滞留 42 小时、投诉 1 次', '无', '点位距上一站 9.2 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-12 19:00:42'),
(28, 28, 3, 3, '{"loadRate":76.9,"stayHours":9.7,"complaints":3,"vehicleCapacity":5.0,"distanceKm":9.2,"typeMatch":0}', 76.9, 9.7, 3, 5.0, 9.2, 0, 20.0, 3.2, 9.6, 6.9, 3.9, 0, 43.6, 'NONE', '满载度 77%、滞留 10 小时、投诉 3 次', '无', '点位距上一站 9.2 km，建议调整线路顺序减少空驶', 0, 1, '原定车辆年检到期，改派同载重车辆', '2026-10-13 21:30:49'),
(29, 29, 3, 3, '{"loadRate":81.6,"stayHours":22.2,"complaints":1,"vehicleCapacity":8.0,"distanceKm":10.2,"typeMatch":1}', 81.6, 22.2, 1, 8.0, 10.2, 1, 21.2, 7.4, 3.2, 2.6, 3.2, 6, 43.6, 'NONE', '满载度 82%、滞留 22 小时、投诉 1 次', '无', '点位距上一站 10.2 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-14 23:45:30'),
(30, 30, 3, 3, '{"loadRate":77.8,"stayHours":15.7,"complaints":2,"vehicleCapacity":8.0,"distanceKm":10.5,"typeMatch":1}', 77.8, 15.7, 2, 8.0, 10.5, 1, 20.2, 5.2, 6.4, 0, 3.0, 6, 40.8, 'NONE', '满载度 78%、滞留 16 小时、投诉 2 次', '车辆剩余容量不足', '点位距上一站 10.5 km，建议调整线路顺序减少空驶', 1, 0, NULL, '2026-10-15 18:30:09');

INSERT INTO dispatch_rule (id, rule_name, version, w_load, w_stay, w_complaint, w_capacity, w_distance, w_type_match, threshold_p1, threshold_p2, threshold_p3, review_threshold, enabled, effective_time, create_by, create_time) VALUES
(1, '容量与时效联合调度规则', 1, 22, 26, 14, 20, 12, 6, 85, 65, 45, 5, 0, '2026-06-15 14:00:00', '系统初始化', '2026-07-03 10:00:51'),
(2, '容量与时效联合调度规则', 2, 24, 24, 16, 18, 12, 6, 85, 65, 45, 5, 0, '2026-09-01 10:20:00', '周建明', '2026-07-03 10:00:55'),
(3, '容量与时效联合调度规则', 3, 26, 24, 16, 18, 10, 6, 85, 65, 45, 5, 1, '2026-10-20 09:00:00', '周建明', '2026-07-03 10:00:31');

INSERT INTO overflow_report (id, report_no, point_id, overflow_level, estimated_weight, image, description, urgency_score, reporter_id, report_time, status, order_id, create_time) VALUES
(1, 'OF20261023-001', 4, 'OBVIOUS', 10.34, '/uploads/seed/site/02.jpg', '清运后未及时清扫', 55.29, 4, '2026-10-23 17:48:53', 'PENDING', NULL, '2026-10-23 17:48:53'),
(2, 'OF20261029-002', 7, 'SERIOUS', 5.44, '/uploads/seed/site/01.jpg', '清运后未及时清扫', 56.74, 4, '2026-10-29 11:58:46', 'DISPATCHED', 2, '2026-10-29 11:58:46'),
(3, 'OF20260921-003', 10, 'LIGHT', 3.56, '/uploads/seed/site/02.jpg', '垃圾桶已满溢出桶口', 75.1, 4, '2026-09-21 14:49:33', 'DONE', 3, '2026-09-21 14:49:33'),
(4, 'OF20260926-004', 13, 'OBVIOUS', 3.19, '/uploads/seed/site/01.jpg', '垃圾落地堆积影响通行', 46.12, 4, '2026-09-26 12:11:34', 'DONE', 4, '2026-09-26 12:11:34'),
(5, 'OF20260930-005', 16, 'SERIOUS', 4.06, '/uploads/seed/site/02.jpg', '异味明显居民反映强烈', 76.53, 4, '2026-09-30 16:56:06', 'CANCELED', 5, '2026-09-30 16:56:06'),
(6, 'OF20261006-006', 19, 'LIGHT', 7.88, '/uploads/seed/site/01.jpg', '垃圾桶已满溢出桶口', 62.47, 4, '2026-10-06 16:38:34', 'PENDING', NULL, '2026-10-06 16:38:34'),
(7, 'OF20260924-007', 2, 'OBVIOUS', 5.59, '/uploads/seed/site/02.jpg', '垃圾桶已满溢出桶口', 87.16, 4, '2026-09-24 15:04:41', 'PENDING', NULL, '2026-09-24 15:04:41'),
(8, 'OF20260923-008', 5, 'SERIOUS', 3.84, '/uploads/seed/site/01.jpg', '垃圾落地堆积影响通行', 94.15, 4, '2026-09-23 18:58:40', 'DISPATCHED', 8, '2026-09-23 18:58:40'),
(9, 'OF20261018-009', 8, 'LIGHT', 6.41, '/uploads/seed/site/02.jpg', '垃圾落地堆积影响通行', 59.23, 4, '2026-10-18 17:58:03', 'DONE', 9, '2026-10-18 17:58:03'),
(10, 'OF20260928-010', 11, 'OBVIOUS', 4.41, '/uploads/seed/site/01.jpg', '垃圾落地堆积影响通行', 84.27, 4, '2026-09-28 10:01:53', 'DONE', 10, '2026-09-28 10:01:53'),
(11, 'OF20261006-011', 14, 'SERIOUS', 9.0, '/uploads/seed/site/02.jpg', '异味明显居民反映强烈', 74.9, 4, '2026-10-06 18:54:21', 'CANCELED', 11, '2026-10-06 18:54:21'),
(12, 'OF20261001-012', 17, 'LIGHT', 3.88, '/uploads/seed/site/01.jpg', '清运后未及时清扫', 92.02, 4, '2026-10-01 08:09:16', 'PENDING', NULL, '2026-10-01 08:09:16'),
(13, 'OF20261028-013', 20, 'OBVIOUS', 2.97, '/uploads/seed/site/02.jpg', '异味明显居民反映强烈', 60.97, 4, '2026-10-28 15:18:59', 'PENDING', NULL, '2026-10-28 15:18:59'),
(14, 'OF20261021-014', 3, 'SERIOUS', 2.47, '/uploads/seed/site/01.jpg', '异味明显居民反映强烈', 56.93, 4, '2026-10-21 09:49:07', 'DISPATCHED', 14, '2026-10-21 09:49:07'),
(15, 'OF20261029-015', 6, 'LIGHT', 1.71, '/uploads/seed/site/02.jpg', '垃圾落地堆积影响通行', 66.58, 4, '2026-10-29 19:46:43', 'DONE', 15, '2026-10-29 19:46:43'),
(16, 'OF20261031-016', 9, 'OBVIOUS', 2.82, '/uploads/seed/site/01.jpg', '垃圾落地堆积影响通行', 78.44, 4, '2026-10-31 10:08:51', 'DONE', 16, '2026-10-31 10:08:51'),
(17, 'OF20260928-017', 12, 'SERIOUS', 3.27, '/uploads/seed/site/02.jpg', '异味明显居民反映强烈', 90.38, 4, '2026-09-28 10:29:46', 'CANCELED', 17, '2026-09-28 10:29:46'),
(18, 'OF20261025-018', 15, 'LIGHT', 3.43, '/uploads/seed/site/01.jpg', '垃圾桶已满溢出桶口', 93.65, 4, '2026-10-25 09:50:27', 'PENDING', NULL, '2026-10-25 09:50:27');

INSERT INTO exception_record (id, exception_no, order_id, point_id, type, level, description, image, reporter, handler, handle_result, status, create_time, update_time) VALUES
(1, 'EX20260001', 4, 8, 'UNREACHABLE', 'LOW', '巷道被私家车占用，车辆无法进入', '/uploads/seed/site/02.jpg', '黄志明', '李振华', '已协调社区清理通道后重新到场', 'HANDLING', '2026-10-07 14:10:52', '2026-10-28 17:20:19'),
(2, 'EX20260002', 7, 15, 'OVERLOAD', 'HIGH', '实际重量超出车辆额定载重 8%', '/uploads/seed/site/01.jpg', '王建军', '李振华', '已分两次转运，超载部分留待下趟', 'CLOSED', '2026-10-30 15:10:54', '2026-10-02 18:20:47'),
(3, 'EX20260003', 10, 2, 'MISS_STOP', 'LOW', '站点遗漏未清运，居民投诉', '/uploads/seed/site/02.jpg', '刘海涛', '李振华', '已补派车辆当日完成清运', 'CLOSED', '2026-10-14 15:10:16', '2026-10-14 12:20:57'),
(4, 'EX20260004', 13, 9, 'OTHER', 'HIGH', '处置场排队时间过长', '/uploads/seed/site/01.jpg', '李国强', NULL, NULL, 'OPEN', '2026-10-01 11:10:24', '2026-10-12 17:20:04'),
(5, 'EX20260005', 16, 16, 'VEHICLE_FAULT', 'HIGH', '车辆行驶中液压系统故障，无法继续作业', '/uploads/seed/site/02.jpg', '徐立新', '李振华', '已改派粤A·D8836接续作业', 'HANDLING', '2026-10-09 11:10:40', '2026-10-05 19:20:49'),
(6, 'EX20260006', 19, 3, 'UNREACHABLE', 'MID', '巷道被私家车占用，车辆无法进入', '/uploads/seed/site/01.jpg', '赵德胜', '李振华', '已协调社区清理通道后重新到场', 'CLOSED', '2026-10-30 18:10:34', '2026-10-31 16:20:05'),
(7, 'EX20260007', 22, 10, 'OVERLOAD', 'HIGH', '实际重量超出车辆额定载重 8%', '/uploads/seed/site/02.jpg', '孙建平', '李振华', '已分两次转运，超载部分留待下趟', 'CLOSED', '2026-10-02 13:10:12', '2026-10-26 09:20:39'),
(8, 'EX20260008', 25, 17, 'MISS_STOP', 'LOW', '站点遗漏未清运，居民投诉', '/uploads/seed/site/01.jpg', '陈伟强', NULL, NULL, 'OPEN', '2026-09-29 09:10:17', '2026-10-10 13:20:32'),
(9, 'EX20260009', 28, 4, 'OTHER', 'LOW', '处置场排队时间过长', '/uploads/seed/site/02.jpg', '黄志明', '李振华', '已调整计划时间避开高峰', 'HANDLING', '2026-10-21 14:10:39', '2026-10-14 10:20:42'),
(10, 'EX20260010', 31, 11, 'VEHICLE_FAULT', 'MID', '车辆行驶中液压系统故障，无法继续作业', '/uploads/seed/site/01.jpg', '王建军', '李振华', '已改派粤A·D8836接续作业', 'CLOSED', '2026-09-26 11:10:56', '2026-10-24 13:20:31'),
(11, 'EX20260011', 34, 18, 'UNREACHABLE', 'LOW', '巷道被私家车占用，车辆无法进入', '/uploads/seed/site/02.jpg', '刘海涛', '李振华', '已协调社区清理通道后重新到场', 'CLOSED', '2026-10-18 15:10:49', '2026-10-13 15:20:18'),
(12, 'EX20260012', 3, 5, 'OVERLOAD', 'HIGH', '实际重量超出车辆额定载重 8%', '/uploads/seed/site/01.jpg', '李国强', NULL, NULL, 'OPEN', '2026-10-12 15:10:17', '2026-10-17 11:20:25');

INSERT INTO vehicle_maintenance (id, vehicle_id, maintain_type, maintain_date, mileage, next_date, next_mileage, cost, status, remark, create_time) VALUES
(1, 4, '年检', '2026-05-29', 36, '2026-08-27', 8036, 1956.39, 'DUE', '距下次保养不足 20 天', '2026-05-29 09:30:26'),
(2, 7, '维修', '2026-09-27', -6, '2026-12-26', 7994, 6095.47, 'DONE', '按期完成', '2026-09-27 09:30:00'),
(3, 10, '常规保养', '2026-05-17', 41, '2026-08-15', 8041, 8334.09, 'DUE', '距下次保养不足 20 天', '2026-05-17 09:30:27'),
(4, 3, '年检', '2026-09-20', 20, '2026-12-19', 8020, 3991.21, 'DONE', '按期完成', '2026-09-20 09:30:00'),
(5, 6, '维修', '2026-09-15', 54, '2026-12-14', 8054, 1309.29, 'DONE', '按期完成', '2026-09-15 09:30:59'),
(6, 9, '常规保养', '2026-04-14', 15, '2026-07-13', 8015, 5081.78, 'DUE', '距下次保养不足 20 天', '2026-04-14 09:30:57'),
(7, 2, '年检', '2026-03-26', 8, '2026-06-24', 8008, 3660.52, 'DUE', '距下次保养不足 20 天', '2026-03-26 09:30:16'),
(8, 5, '维修', '2026-07-19', 3, '2026-10-17', 8003, 1952.93, 'ING', '保养中，暂停派单', '2026-07-19 09:30:36'),
(9, 8, '常规保养', '2026-03-07', 88, '2026-06-05', 8088, 3472.82, 'DUE', '距下次保养不足 20 天', '2026-03-07 09:30:25'),
(10, 1, '年检', '2026-05-28', 12, '2026-08-26', 8012, 3406.43, 'DUE', '距下次保养不足 20 天', '2026-05-28 09:30:08'),
(11, 4, '维修', '2026-03-01', 36, '2026-05-30', 8036, 6297.2, 'DUE', '距下次保养不足 20 天', '2026-03-01 09:30:05'),
(12, 7, '常规保养', '2026-08-10', -6, '2026-11-08', 7994, 2589.26, 'DUE', '距下次保养不足 20 天', '2026-08-10 09:30:53'),
(13, 10, '年检', '2026-05-24', 41, '2026-08-22', 8041, 904.08, 'DUE', '距下次保养不足 20 天', '2026-05-24 09:30:47'),
(14, 3, '维修', '2026-06-20', 20, '2026-09-18', 8020, 8483.07, 'DUE', '距下次保养不足 20 天', '2026-06-20 09:30:43');

INSERT INTO attachment (id, biz_type, biz_id, file_name, file_path, file_size, uploader, create_time) VALUES
(1, 'DISPATCH', 1, 'site-QD20260917-0001-1.jpg', '/uploads/seed/site/01.jpg', 219297, '徐立新', '2026-09-17 16:00:28'),
(2, 'DISPATCH', 2, 'site-QD20260918-0002-1.jpg', '/uploads/seed/site/02.jpg', 237684, '王建军', '2026-09-18 10:45:30'),
(3, 'DISPATCH', 3, 'site-QD20260919-0003-1.jpg', '/uploads/seed/site/01.jpg', 181962, '孙建平', '2026-09-19 10:30:56'),
(4, 'DISPATCH', 4, 'site-QD20260920-0004-1.jpg', '/uploads/seed/site/02.jpg', 305993, '李国强', '2026-09-20 08:00:18'),
(5, 'DISPATCH', 5, 'site-QD20260921-0005-1.jpg', '/uploads/seed/site/01.jpg', 247410, '黄志明', '2026-09-21 15:30:05'),
(6, 'DISPATCH', 5, 'site-QD20260921-0005-2.jpg', '/uploads/seed/site/01.jpg', 261338, '黄志明', '2026-09-21 15:30:05'),
(7, 'DISPATCH', 5, 'site-QD20260921-0005-3.jpg', '/uploads/seed/site/01.jpg', 203989, '黄志明', '2026-09-21 15:30:05'),
(8, 'DISPATCH', 6, 'site-QD20260922-0006-1.jpg', '/uploads/seed/site/02.jpg', 293183, '赵德胜', '2026-09-22 11:30:21'),
(9, 'DISPATCH', 7, 'site-QD20260923-0007-1.jpg', '/uploads/seed/site/01.jpg', 241341, '刘海涛', '2026-09-23 12:15:34'),
(10, 'DISPATCH', 8, 'site-QD20260924-0008-1.jpg', '/uploads/seed/site/02.jpg', 214492, '陈伟强', '2026-09-24 15:30:43'),
(11, 'DISPATCH', 9, 'site-QD20260925-0009-1.jpg', '/uploads/seed/site/01.jpg', 203193, '徐立新', '2026-09-25 15:15:24'),
(12, 'DISPATCH', 10, 'site-QD20260926-0010-1.jpg', '/uploads/seed/site/02.jpg', 304147, '王建军', '2026-09-26 12:45:03'),
(13, 'DISPATCH', 10, 'site-QD20260926-0010-2.jpg', '/uploads/seed/site/02.jpg', 193686, '王建军', '2026-09-26 12:45:03'),
(14, 'DISPATCH', 10, 'site-QD20260926-0010-3.jpg', '/uploads/seed/site/02.jpg', 199186, '王建军', '2026-09-26 12:45:03'),
(15, 'DISPATCH', 11, 'site-QD20260927-0011-1.jpg', '/uploads/seed/site/01.jpg', 267026, '孙建平', '2026-09-27 12:15:34'),
(16, 'DISPATCH', 12, 'site-QD20260928-0012-1.jpg', '/uploads/seed/site/02.jpg', 283275, '李国强', '2026-09-28 10:30:51'),
(17, 'DISPATCH', 13, 'site-QD20260929-0013-1.jpg', '/uploads/seed/site/01.jpg', 216977, '黄志明', '2026-09-29 12:15:16'),
(18, 'DISPATCH', 14, 'site-QD20260930-0014-1.jpg', '/uploads/seed/site/02.jpg', 286601, '赵德胜', '2026-09-30 07:15:35'),
(19, 'DISPATCH', 15, 'site-QD20261001-0015-1.jpg', '/uploads/seed/site/01.jpg', 301304, '刘海涛', '2026-10-01 10:15:44'),
(20, 'DISPATCH', 15, 'site-QD20261001-0015-2.jpg', '/uploads/seed/site/01.jpg', 311484, '刘海涛', '2026-10-01 10:15:44'),
(21, 'DISPATCH', 15, 'site-QD20261001-0015-3.jpg', '/uploads/seed/site/01.jpg', 251743, '刘海涛', '2026-10-01 10:15:44'),
(22, 'DISPATCH', 16, 'site-QD20261002-0016-1.jpg', '/uploads/seed/site/02.jpg', 202152, '陈伟强', '2026-10-02 14:15:20'),
(23, 'DISPATCH', 17, 'site-QD20261003-0017-1.jpg', '/uploads/seed/site/01.jpg', 276648, '徐立新', '2026-10-03 08:45:55'),
(24, 'DISPATCH', 18, 'site-QD20261004-0018-1.jpg', '/uploads/seed/site/02.jpg', 237918, '王建军', '2026-10-04 10:00:07'),
(25, 'DISPATCH', 19, 'site-QD20261005-0019-1.jpg', '/uploads/seed/site/01.jpg', 203887, '孙建平', '2026-10-05 16:45:37'),
(26, 'DISPATCH', 20, 'site-QD20261006-0020-1.jpg', '/uploads/seed/site/02.jpg', 273358, '李国强', '2026-10-06 14:45:18'),
(27, 'DISPATCH', 20, 'site-QD20261006-0020-2.jpg', '/uploads/seed/site/02.jpg', 264639, '李国强', '2026-10-06 14:45:18'),
(28, 'DISPATCH', 20, 'site-QD20261006-0020-3.jpg', '/uploads/seed/site/02.jpg', 235190, '李国强', '2026-10-06 14:45:18');

INSERT INTO sys_message (id, title, content, biz_type, biz_no, receiver_id, read_flag, create_time) VALUES
(1, '待派车提醒', '任务 QD20261031-0012 已生成，满载度 92% 超过阈值，请尽快派车', 'DISPATCH', 'QD20261031-0012', 2, 0, '2026-10-30 09:04:09'),
(2, '异常上报', '任务 QD20261030-0086 上报车辆故障，已暂停执行', 'EXCEPTION', 'QD20261030-0086', 2, 0, '2026-10-29 09:08:13'),
(3, '净重复核提醒', '称重单 WJ20261028-004 净重偏差 6.8%，请复核', 'WEIGHING', 'WJ20261028-004', 1, 0, '2026-10-28 09:12:44'),
(4, '报满提醒', '锦绣花园小区北门站上报明显满溢，请安排清运', 'OVERFLOW', 'OF20261031-006', 2, 0, '2026-10-27 09:16:27'),
(5, '任务已派发', '您有新任务 QD20261031-0014，计划 11:40 到场', 'DISPATCH', 'QD20261031-0014', 7, 1, '2026-10-26 09:20:16'),
(6, '保养到期提醒', '粤A·D8890 距下次保养不足 20 天', 'MAINTAIN', '粤A·D8890', 1, 1, '2026-10-25 09:24:02'),
(7, '任务退回', '任务 QD20261029-0021 因现场无法进入被退回', 'DISPATCH', 'QD20261029-0021', 7, 1, '2026-10-24 09:28:14'),
(8, '规则版本变更', '调度规则已升级至 v3，新计算将使用新权重', 'RULE', 'v3', 2, 1, '2026-10-23 09:32:32'),
(9, '任务待确认', '任务 QD20261030-0087 已完成，请确认交接', 'DISPATCH', 'QD20261030-0087', 2, 1, '2026-10-22 09:36:40'),
(10, '投诉转办', '城南农贸市场东门站收到异味投诉，请跟进', 'COMPLAINT', 'CP-2026-0031', 4, 1, '2026-10-21 09:40:33');

INSERT INTO sys_log (id, user_id, user_name, module, action, method, params, ip, cost_ms, create_time) VALUES
(1, 2, '李振华', '清运调度台', '派车', 'POST /api/dispatch/action', '{}', '127.0.0.1', 221, '2026-10-29 18:04:38'),
(2, 3, '何晓雯', '称重交接', '确认交接', 'POST /api/common/action', '{}', '127.0.0.1', 415, '2026-10-08 14:38:52'),
(3, 4, '王秀兰', '调度规则配置', '保存规则', 'POST /api/common/action', '{}', '127.0.0.1', 45, '2026-10-22 10:26:34'),
(4, 5, '李国庆', '异常处理', '处理异常', 'POST /api/common/action', '{}', '127.0.0.1', 396, '2026-10-30 14:48:30'),
(5, 6, '刘敏', '临时报满', '提交上报', 'POST /api/common/action', '{}', '127.0.0.1', 87, '2026-10-16 13:09:14'),
(6, 7, '陈伟强', '车辆档案', '编辑车辆', 'POST /api/common/action', '{}', '127.0.0.1', 240, '2026-10-01 17:44:13'),
(7, 8, '黄志明', '用户管理', '重置密码', 'POST /api/common/action', '{}', '127.0.0.1', 226, '2026-10-16 18:39:56'),
(8, 9, '王建军', '收集点管理', '新增收集点', 'POST /api/common/action', '{}', '127.0.0.1', 258, '2026-10-14 08:55:25'),
(9, 10, '刘海涛', '清运调度台', '派车', 'POST /api/dispatch/action', '{}', '127.0.0.1', 221, '2026-10-09 08:14:22'),
(10, 11, '李国强', '称重交接', '确认交接', 'POST /api/common/action', '{}', '127.0.0.1', 377, '2026-10-13 13:29:28'),
(11, 12, '孙志刚', '调度规则配置', '保存规则', 'POST /api/common/action', '{}', '127.0.0.1', 357, '2026-10-08 19:40:13'),
(12, 1, '周建明', '异常处理', '处理异常', 'POST /api/common/action', '{}', '127.0.0.1', 273, '2026-10-18 19:10:48'),
(13, 2, '李振华', '临时报满', '提交上报', 'POST /api/common/action', '{}', '127.0.0.1', 23, '2026-10-27 09:14:20'),
(14, 3, '何晓雯', '车辆档案', '编辑车辆', 'POST /api/common/action', '{}', '127.0.0.1', 159, '2026-10-01 11:47:21'),
(15, 4, '王秀兰', '用户管理', '重置密码', 'POST /api/common/action', '{}', '127.0.0.1', 48, '2026-10-03 14:59:30'),
(16, 5, '李国庆', '收集点管理', '新增收集点', 'POST /api/common/action', '{}', '127.0.0.1', 71, '2026-10-15 10:49:39'),
(17, 6, '刘敏', '清运调度台', '派车', 'POST /api/dispatch/action', '{}', '127.0.0.1', 203, '2026-10-19 15:09:38'),
(18, 7, '陈伟强', '称重交接', '确认交接', 'POST /api/common/action', '{}', '127.0.0.1', 260, '2026-10-07 08:11:14'),
(19, 8, '黄志明', '调度规则配置', '保存规则', 'POST /api/common/action', '{}', '127.0.0.1', 147, '2026-10-19 12:02:12'),
(20, 9, '王建军', '异常处理', '处理异常', 'POST /api/common/action', '{}', '127.0.0.1', 309, '2026-10-02 14:48:56'),
(21, 10, '刘海涛', '临时报满', '提交上报', 'POST /api/common/action', '{}', '127.0.0.1', 100, '2026-10-10 13:00:24'),
(22, 11, '李国强', '车辆档案', '编辑车辆', 'POST /api/common/action', '{}', '127.0.0.1', 361, '2026-10-17 19:54:47'),
(23, 12, '孙志刚', '用户管理', '重置密码', 'POST /api/common/action', '{}', '127.0.0.1', 368, '2026-10-02 08:33:25'),
(24, 1, '周建明', '收集点管理', '新增收集点', 'POST /api/common/action', '{}', '127.0.0.1', 311, '2026-10-16 16:21:44'),
(25, 2, '李振华', '清运调度台', '派车', 'POST /api/dispatch/action', '{}', '127.0.0.1', 416, '2026-10-16 18:27:17'),
(26, 3, '何晓雯', '称重交接', '确认交接', 'POST /api/common/action', '{}', '127.0.0.1', 66, '2026-10-07 17:47:41'),
(27, 4, '王秀兰', '调度规则配置', '保存规则', 'POST /api/common/action', '{}', '127.0.0.1', 130, '2026-10-25 09:38:38'),
(28, 5, '李国庆', '异常处理', '处理异常', 'POST /api/common/action', '{}', '127.0.0.1', 154, '2026-10-06 19:14:58'),
(29, 6, '刘敏', '临时报满', '提交上报', 'POST /api/common/action', '{}', '127.0.0.1', 338, '2026-10-27 11:39:17'),
(30, 7, '陈伟强', '车辆档案', '编辑车辆', 'POST /api/common/action', '{}', '127.0.0.1', 367, '2026-10-08 19:56:28'),
(31, 8, '黄志明', '用户管理', '重置密码', 'POST /api/common/action', '{}', '127.0.0.1', 165, '2026-10-29 18:47:49'),
(32, 9, '王建军', '收集点管理', '新增收集点', 'POST /api/common/action', '{}', '127.0.0.1', 352, '2026-10-23 16:32:07'),
(33, 10, '刘海涛', '清运调度台', '派车', 'POST /api/dispatch/action', '{}', '127.0.0.1', 388, '2026-10-03 09:28:28'),
(34, 11, '李国强', '称重交接', '确认交接', 'POST /api/common/action', '{}', '127.0.0.1', 116, '2026-10-19 18:16:57'),
(35, 12, '孙志刚', '调度规则配置', '保存规则', 'POST /api/common/action', '{}', '127.0.0.1', 152, '2026-10-11 09:02:19'),
(36, 1, '周建明', '异常处理', '处理异常', 'POST /api/common/action', '{}', '127.0.0.1', 85, '2026-10-11 13:10:32'),
(37, 2, '李振华', '临时报满', '提交上报', 'POST /api/common/action', '{}', '127.0.0.1', 398, '2026-10-15 13:08:42'),
(38, 3, '何晓雯', '车辆档案', '编辑车辆', 'POST /api/common/action', '{}', '127.0.0.1', 340, '2026-10-26 10:10:23'),
(39, 4, '王秀兰', '用户管理', '重置密码', 'POST /api/common/action', '{}', '127.0.0.1', 64, '2026-10-14 17:38:06'),
(40, 5, '李国庆', '收集点管理', '新增收集点', 'POST /api/common/action', '{}', '127.0.0.1', 383, '2026-10-06 12:00:12');

-- 校验：菜单管理自身隐藏、每条任务的状态与站点/称重数据一致
SELECT '收集点' AS t, COUNT(*) c FROM collection_point
UNION ALL SELECT '清运任务', COUNT(*) FROM dispatch_order
UNION ALL SELECT '任务站点', COUNT(*) FROM route_stop
UNION ALL SELECT '称重记录', COUNT(*) FROM weighing_record
UNION ALL SELECT '计算留痕', COUNT(*) FROM dispatch_score;
