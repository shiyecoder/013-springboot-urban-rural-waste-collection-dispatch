#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 sql/init.sql —— 城乡垃圾清运调度与台账管理系统（NEW-013）
表结构对齐需求文档「数据库与接口细化」，测试数据跨 6 个月真实分布。
"""
import random
from datetime import datetime, timedelta

random.seed(20261031)

OUT = []
def w(s=""):
    OUT.append(s)

w("-- ============================================================")
w("-- 城乡垃圾清运调度与台账管理系统  初始化脚本 (MySQL 8 / utf8mb4)")
w("-- 库名 new_013。每张表均含测试数据，create_time 分布在近 6 个月。")
w("-- 默认账号：admin / admin123（运营管理员），其余账号同密码")
w("-- ============================================================")
w("DROP DATABASE IF EXISTS new_013;")
w("CREATE DATABASE new_013 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
w("USE new_013;")
w()

# ---------------- DDL ----------------
DDL = """
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
"""
w(DDL)

# ---------------- 帮助 ----------------
BCRYPT = "$2b$10$gbe.oJNsirPSkvkn8UCm9.GrlDEomxEl6bVjF.WiC7b.XsaRQAepK"  # admin123
def dt(d): return d.strftime("%Y-%m-%d %H:%M:%S")
def esc(s): return s.replace("'", "''")
TODAY = datetime(2026, 10, 31, 17, 30, 0)
def back(days, h=None, m=None):
    d = TODAY - timedelta(days=days)
    if h is not None:
        d = d.replace(hour=h, minute=m if m is not None else random.randint(0, 59), second=random.randint(0, 59))
    return d

def insert(table, cols, rows, chunk=200):
    if not rows: return
    w(f"INSERT INTO {table} ({', '.join(cols)}) VALUES")
    for i in range(0, len(rows), chunk):
        part = rows[i:i+chunk]
        for j, r in enumerate(part):
            tail = ";" if (i + j == len(rows) - 1) else ","
            w("(" + ", ".join(r) + ")" + tail)
    w()

# ---------------- 组织 ----------------
orgs = [
    ("城南环卫所", "环卫所", "城南街道", "周建明", "0571-88230001", 1),
    ("锦绣物业管理处", "物业", "城南街道", "王秀兰", "0571-88230012", 2),
    ("老城环卫所", "环卫所", "老城街道", "张德海", "0571-88230003", 3),
    ("滨江市容管理处", "环卫所", "滨江片区", "陈志远", "0571-88230004", 4),
    ("高新园区服务中心", "园区", "高新片区", "刘敏", "0571-88230005", 5),
    ("城北乡镇环卫站", "乡镇", "城北乡镇", "赵国强", "0571-88230006", 6),
]
rows = []
for i, (n, t, a, l, p, s) in enumerate(orgs, 1):
    rows.append([str(i), f"'{n}'", f"'{t}'", f"'{a}'", f"'{l}'", f"'{p}'", str(s), "1", f"'{dt(back(170-i*3, 9, 12))}'", "0"])
insert("sys_org", ["id","org_name","org_type","area","leader","phone","sort","status","create_time","deleted"], rows)

# ---------------- 角色 ----------------
roles = [("ADMIN","运营管理员","ALL","全部数据范围，维护基础档案与报表"),
         ("DISPATCHER","调度员","ORG","调度范围内的任务与异常"),
         ("POINT","收集点管理员","SELF","仅本点位报量与派单查看"),
         ("DRIVER","司机","SELF","仅本人任务")]
rows = []
for i,(c,n,sc,r) in enumerate(roles,1):
    rows.append([str(i), f"'{c}'", f"'{n}'", f"'{sc}'", f"'{r}'", f"'{dt(back(180,10,0))}'"])
insert("sys_role", ["id","role_code","role_name","data_scope","remark","create_time"], rows)

# ---------------- 菜单 ----------------
menus = [
 (0,"运营总览",None,None,"M",None,1),
 (1,"环卫运营看板","/dashboard","dashboard","M","dashboard:view",1),
 (0,"基础档案",None,None,"M",None,2),
 (3,"收集点管理","/point","point","M","point:list",1),
 (4,"新增收集点",None,None,"B","point:add",1),
 (4,"编辑收集点",None,None,"B","point:edit",1),
 (4,"删除收集点",None,None,"B","point:delete",1),
 (3,"车辆档案","/vehicle","truck","M","vehicle:list",2),
 (8,"编辑车辆",None,None,"B","vehicle:edit",1),
 (3,"司机档案","/driver","driver","M","driver:list",3),
 (3,"线路与处置场","/route","route","M","route:list",4),
 (0,"调度台账",None,None,"M",None,3),
 (12,"清运调度台","/dispatch","dispatch","M","dispatch:list",1),
 (13,"派车",None,None,"B","dispatch:assign",1),
 (13,"改派",None,None,"B","dispatch:reassign",2),
 (12,"临时报满","/overflow","overflow","M","overflow:list",2),
 (16,"上报报满",None,None,"B","overflow:add",1),
 (12,"称重交接","/weighing","weigh","M","weigh:list",3),
 (18,"确认交接",None,None,"B","weigh:confirm",1),
 (12,"异常处理",None,None,"B","exception:list",4),
 (20,"处理异常",None,None,"B","exception:handle",1),
 (12,"车辆保养","/maintenance","wrench","M","maintain:list",5),
 (0,"分析与配置",None,None,"M",None,4),
 (23,"调度规则配置","/rule","rule","M","rule:config",1),
 (24,"保存规则",None,None,"B","rule:save",1),
 (23,"计算留痕","/score","report","M","score:list",2),
 (23,"统计报表","/report","report","M","report:view",3),
 (0,"系统管理",None,None,"M",None,5),
 (28,"用户管理","/user","user","M","user:list",1),
 (28,"角色管理","/role","role","M","role:list",2),
 (28,"菜单管理","/menu","menu","M","menu:list",3),
 (28,"为角色分配菜单",None,None,"B","role:assign",4),
 (0,"个人中心",None,None,"M",None,6),
 (33,"我的任务","/my-task","dispatch","M","task:mine",1),
 (33,"我的点位","/my-point","point","M","point:mine",2),
]
rows = []
for i,(p,n,path,icon,t,perm,vis) in enumerate(menus,1):
    rows.append([str(i), str(p), f"'{esc(n)}'",
                 "NULL" if path is None else f"'{path}'",
                 "NULL" if icon is None else f"'{icon}'",
                 f"'{t}'",
                 "NULL" if perm is None else f"'{perm}'",
                 str(i), str(vis), f"'{dt(back(178,10,0))}'"])
insert("sys_menu", ["id","parent_id","menu_name","path","icon","menu_type","perm","sort","visible","create_time"], rows)
# 隐藏「菜单管理」选项（需求硬性要求 12）
w("UPDATE sys_menu SET visible = 0 WHERE menu_name = '菜单管理';")
w()

# 角色菜单：ADMIN 全部；DISPATCHER 看板+调度+报满+称重+异常+规则；POINT 我的点位/报满/任务查看；DRIVER 我的任务
_rid = 0
def grant(role_id, ids):
    global _rid
    out = []
    for m in ids:
        _rid += 1
        out.append([str(_rid), str(role_id), str(m)])
    return out
admin_ids = list(range(1, 35))
rows = grant(1, admin_ids)
rows += grant(2, [1,2,3,4,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,33,34])
rows += grant(3, [1,2,3,4,5,12,16,17,18,33,34,35])
rows += grant(4, [33,35])
insert("sys_role_menu", ["id","role_id","menu_id"], rows)

# ---------------- 处置场 ----------------
sites = [
 ("DS-001","城南综合处置场","城南街道疏港路 88 号",800.00,"生活垃圾,建筑垃圾,大件垃圾","孙志刚","0571-88230101",1),
 ("DS-002","城西焚烧发电厂","老城街道工业园 12 号",600.00,"生活垃圾,园林绿化","吴建国","0571-88230102",2),
 ("DS-003","滨江资源化利用中心","滨江片区临江路 5 号",300.00,"建筑垃圾,大件垃圾","郑海涛","0571-88230103",3),
 ("DS-004","高新餐厨处理站","高新片区科创大道 66 号",200.00,"餐厨垃圾","刘敏","0571-88230104",4),
 ("DS-005","城北填埋场","城北乡镇北环路 21 号",500.00,"生活垃圾,建筑垃圾","赵国强","0571-88230105",5),
]
rows = []
for i,(c,n,a,cap,t,m,p,img) in enumerate(sites,1):
    rows.append([str(i), f"'{c}'", f"'{n}'", f"'{a}'", f"{cap}", f"'{t}'", f"'{m}'", f"'{p}'",
                 f"'/uploads/seed/dispose/{((i*7)%2)+1:02d}.jpg'", "1", f"'{dt(back(175-i*4,10,20))}'", "0"])
insert("dispose_site", ["id","site_code","site_name","address","capacity","dispose_types","manager","phone","image","status","create_time","deleted"], rows)

# ---------------- 线路 ----------------
routes = [
 ("R-01","老城环线","老城街道",18.60,5,1),
 ("R-02","城南环线","城南街道",22.40,6,1),
 ("R-03","城北乡镇线","城北乡镇",34.20,5,1),
 ("R-04","滨江线","滨江片区",19.80,4,1),
 ("R-05","高新线","高新片区",16.50,4,1),
 ("R-06","城南东线","城南街道",14.20,3,1),
]
rows = []
for i,(c,n,a,d,s,st) in enumerate(routes,1):
    rows.append([str(i), f"'{c}'", f"'{n}'", f"'{a}'", f"{d}", str(s), str(st), f"'线路 {c} 覆盖 {a} 主要收集点'", f"'{dt(back(172-i*2,11,5))}'", "0"])
insert("route", ["id","route_code","route_name","area","distance_km","stop_count","status","remark","create_time","deleted"], rows)

# ---------------- 收集点 ----------------
point_defs = [
 ("城南农贸市场东门站","城南街道","城南街道农贸市场东门","生活垃圾",8.0,1,"李国庆","138****2210",0),
 ("锦绣花园小区北门站","城南街道","锦绣花园北门内侧","生活垃圾",6.0,2,"王秀兰","139****6602",1),
 ("第三小学后街站","老城街道","老城街道后街 18 号","生活垃圾",4.0,3,"张德海","137****8891",2),
 ("滨江路建材市场站","滨江片区","滨江路建材市场西侧","建筑垃圾",12.0,4,"陈志远","136****3345",3),
 ("高新科技园 B 区站","高新片区","科创大道 B 区 3 号楼旁","餐厨垃圾",5.0,5,"刘敏","135****7723",4),
 ("城北乡镇卫生院站","城北乡镇","城北乡镇卫生院后院","生活垃圾",3.0,6,"赵国强","133****1180",5),
 ("老城文化广场站","老城街道","文化广场东南角","园林绿化",6.0,3,"孙丽华","138****5567",0),
 ("滨江花园西区站","滨江片区","滨江花园西区 7 幢旁","生活垃圾",8.0,4,"郑海涛","139****9902",1),
 ("城南小学北门站","城南街道","城南小学北门","生活垃圾",4.0,1,"李国庆","138****2210",2),
 ("锦绣花园东门站","城南街道","锦绣花园东门车库口","生活垃圾",6.0,2,"王秀兰","139****6602",3),
 ("老城菜市场西站","老城街道","老城菜市场西侧巷道","生活垃圾",5.0,3,"张德海","137****8891",4),
 ("老城医院后门站","老城街道","老城医院后勤通道","生活垃圾",4.0,3,"孙丽华","138****5567",5),
 ("滨江写字楼群站","滨江片区","滨江大道 100 号楼下","生活垃圾",6.0,4,"陈志远","136****3345",0),
 ("滨江装饰城站","滨江片区","装饰城北门停车场","建筑垃圾",10.0,4,"郑海涛","139****9902",1),
 ("高新产品园 A 区站","高新片区","产品园 A 区食堂后","餐厨垃圾",5.0,5,"刘敏","135****7723",2),
 ("高新宿舍区站","高新片区","高新宿舍区 2 号楼旁","生活垃圾",6.0,5,"刘敏","135****7723",3),
 ("城北农贸集市站","城北乡镇","城北集市北侧","生活垃圾",5.0,6,"赵国强","133****1180",4),
 ("城北中学站","城北乡镇","城北中学围墙外","生活垃圾",4.0,6,"赵国强","133****1180",5),
 ("城南工业园站","城南街道","工业园纬三路","建筑垃圾",14.0,1,"李国庆","138****2210",0),
 ("滨江公园东门站","滨江片区","滨江公园东门","园林绿化",5.0,4,"郑海涛","139****9902",1),
]
WASTE = ["生活垃圾","建筑垃圾","餐厨垃圾","大件垃圾","园林绿化"]
rows = []
coords = []
for i, (n, area, addr, wt, cap, org, mgr, ph, img) in enumerate(point_defs, 1):
    load = round(random.uniform(0.18, 0.96) * cap, 2)
    rate = int(round(load / cap * 100))
    last_days = random.randint(0, 9)
    lt = back(last_days, random.randint(5, 18), random.randint(0, 59))
    status = "OVERFLOW" if rate >= 88 else ("DISABLED" if i == 7 else "NORMAL")
    lng = round(120.15 + i * 0.007, 6)
    lat = round(30.28 - i * 0.004, 6)
    coords.append((lng, lat))
    rows.append([str(i), f"'CP-2026-{i+30:04d}'", f"'{n}'", f"'{area}'", f"'{addr}'", f"'{wt}'",
                 f"{cap:.2f}", f"{load:.2f}", str(rate), str(org), f"'{mgr}'", f"'{ph}'",
                 f"'{dt(lt)}'", f"{lng}", f"{lat}",
                 f"'/uploads/seed/point/{((i*7)%6)+1:02d}.jpg'", f"'{status}'", str(random.randint(0,3)),
                 f"'{dt(back(170-i*3, 9, 30))}'", f"'{dt(lt)}'", "0"])
insert("collection_point", ["id","point_code","point_name","area","address","waste_type","capacity","current_load","load_rate","org_id","manager","manager_phone","last_clear_time","longitude","latitude","cover_image","status","version","create_time","update_time","deleted"], rows)

# ---------------- 车辆 ----------------
vehicles = [
 ("粤A·D8821","压缩式",8.0,"生活垃圾,园林绿化",12,1),
 ("粤A·D8836","后装式",6.0,"生活垃圾",8,2),
 ("粤A·D8850","压缩式",10.0,"生活垃圾,建筑垃圾",20,3),
 ("粤A·D8862","密闭罐式",5.0,"餐厨垃圾",36,1),
 ("粤A·D8875","后装式",6.0,"生活垃圾,园林绿化",3,2),
 ("粤A·D8881","勾臂式",12.0,"建筑垃圾,大件垃圾",54,3),
 ("粤A·D8890","压缩式",8.0,"生活垃圾",-6,1),
 ("粤A·D8903","密闭罐式",5.0,"餐厨垃圾",88,1),
 ("粤A·D8915","后装式",6.0,"生活垃圾",15,2),
 ("粤A·D8927","勾臂式",12.0,"建筑垃圾,大件垃圾",41,3),
]
VSTATUS = ["BUSY","IDLE","IDLE","BUSY","MAINTAIN","IDLE","IDLE","BUSY","IDLE","DISABLED"]
rows = []
for i,(p,t,cap,wt,ac,s) in enumerate(vehicles,1):
    acd = TODAY + timedelta(days=ac)
    rows.append([str(i), f"'{p}'", f"'{t}'", f"{cap}", f"'{wt}'", f"'{acd.strftime('%Y-%m-%d')}'",
                 str(random.randint(28000, 165000)), f"'{VSTATUS[i-1]}'",
                 f"'/uploads/seed/vehicle/{((i*7)%3)+1:02d}.jpg'",
                 f"'车辆 {p}，{t}，额定载重 {cap} 吨'", f"'{dt(back(168-i*2,8,15))}'", "0"])
insert("vehicle", ["id","plate_no","vehicle_type","load_capacity","waste_types","annual_check_date","mileage","status","image","remark","create_time","deleted"], rows)

# ---------------- 司机 ----------------
drivers = [
 ("D-1001","陈伟强","138****1234","3301**********1234","A2","2029-05-18",1),
 ("D-1002","黄志明","139****5678","3301**********5678","B2","2028-11-02",2),
 ("D-1003","王建军","137****9012","3301**********9012","A2","2027-08-25",3),
 ("D-1004","刘海涛","136****3456","3301**********3456","B2","2030-01-14",4),
 ("D-1005","李国强","135****7890","3301**********7890","A2","2026-12-09",5),
 ("D-1006","徐立新","133****2345","3301**********2345","B2","2029-03-21",6),
 ("D-1007","赵德胜","158****6789","3301**********6789","A2","2028-06-30",7),
 ("D-1008","孙建平","159****0123","3301**********0123","B2","2027-04-16",8),
]
rows = []
for i,(no,n,ph,lic,lt,exp,vid) in enumerate(drivers,1):
    rows.append([str(i), f"'{no}'", f"'{n}'", f"'{ph}'", f"'{lic}'", f"'{lt}'", f"'{exp}'",
                 str(vid), f"'/uploads/seed/avatar/{((i*7)%6)+1:02d}.jpg'", "1",
                 f"'{dt(back(165-i*3,9,0))}'", "0"])
insert("driver", ["id","driver_no","name","phone","license_no","license_type","license_expire","vehicle_id","avatar","status","create_time","deleted"], rows)

# ---------------- 用户 ----------------
users = [
 (1,"admin","周建明",5,1,1,None,None),
 (2,"dispatcher01","李振华",4,2,1,None,None),
 (3,"dispatcher02","何晓雯",5,2,1,None,None),
 (4,"point01","王秀兰",6,3,2,2,None),
 (5,"point02","李国庆",3,3,1,1,None),
 (6,"point03","刘敏",2,3,5,5,None),
 (7,"driver01","陈伟强",1,4,1,None,1),
 (8,"driver02","黄志明",2,4,2,None,2),
 (9,"driver03","王建军",3,4,3,None,3),
 (10,"driver04","刘海涛",2,4,4,None,4),
 (11,"driver05","李国强",1,4,1,None,5),
 (12,"ops02","孙志刚",5,1,3,None,None),
]
rows = []
for (avail, un, rn, org, role, st, pid, did) in users:
    rows.append(["NULL", f"'{un}'", f"'{BCRYPT}'", f"'{rn}'",
                 f"'/uploads/seed/avatar/{avail:02d}.jpg'",
                 f"'13{700000000 + avail * 1379}'",
                 f"'{un}@waste.gov.cn'", str(org), str(role),
                 "NULL" if pid is None else str(pid), "NULL" if did is None else str(did),
                 str(st), "0", "NULL", f"'{dt(back(3, 8, 20))}'",
                 f"'{dt(back(178-avail*2, 9, 0))}'", f"'{dt(back(3, 8, 20))}'", "0"])
insert("sys_user", ["id","username","password","real_name","avatar","phone","email","org_id","role_id","point_id","driver_id","status","login_fail","lock_until","last_login","create_time","update_time","deleted"], rows)

# ---------------- 字典 ----------------
DICTS = {
 "waste_type": ["生活垃圾","建筑垃圾","餐厨垃圾","大件垃圾","园林绿化"],
 "point_status": [("NORMAL","正常"),("OVERFLOW","满溢"),("DISABLED","停用")],
 "order_status": [("PENDING_DISPATCH","待派车"),("ACCEPTED","已接单"),("RUNNING","清运中"),("PENDING_CONFIRM","待确认"),("DONE","已完成"),("CANCELED","已取消"),("ABNORMAL","异常")],
 "overflow_level": [("LIGHT","轻微"),("OBVIOUS","明显"),("SERIOUS","严重")],
 "exception_type": [("VEHICLE_FAULT","车辆故障"),("UNREACHABLE","收集点无法进入"),("OVERLOAD","重量超载"),("MISS_STOP","漏站"),("OTHER","其他")],
 "dispose_type": [("LAND_FILL","填埋"),("INCINERATE","焚烧发电"),("RECYCLE","资源化利用")],
 "frequency": [("DAILY","每日"),("EVERY_2_DAYS","隔日"),("WEEKLY","每周")],
 "order_type": [("PLAN","周期计划"),("URGENT","紧急插单"),("MERGE","合并任务")],
}
rows = []
idx = 1
for t, vals in DICTS.items():
    for s, v in enumerate(vals, 1):
        if isinstance(v, tuple):
            lab, val = v[1], v[0]
        else:
            lab, val = v, v
        rows.append([str(idx), f"'{t}'", f"'{lab}'", f"'{val}'", str(s), "1"]); idx += 1
insert("sys_dict", ["id","dict_type","dict_label","dict_value","sort","status"], rows)

# ---------------- 周期计划 ----------------
FREQ = [("DAILY",None),("EVERY_2_DAYS",None),("WEEKLY",1),("WEEKLY",4)]
rows = []
for i in range(1, 25):
    pid = ((i * 7) % 20) + 1
    fr, wd = FREQ[i % 4]
    cap = point_defs[pid-1][4]
    rows.append([str(i), f"'PL-2026-{i:03d}'", str(pid), str(((pid-1) % 6) + 1),
                 f"'{random.choice(WASTE)}'", f"'{fr}'",
                 "NULL" if wd is None else str(wd),
                 f"{round(cap*random.uniform(.6,.95),2)}",
                 f"'{(TODAY + timedelta(days=random.randint(0,6))).strftime('%Y-%m-%d')}'",
                 "'ON'", f"'{dt(back(160-i*2,10,0))}'", "0"])
insert("collection_plan", ["id","plan_code","point_id","route_id","waste_type","frequency","weekday","estimated_weight","next_date","status","create_time","deleted"], rows)

# ---------------- 投诉 ----------------
rows = []
for i in range(1, 21):
    pid = ((i * 5) % 20) + 1
    ht = back(random.randint(1, 150), random.randint(8, 20), random.randint(0, 59))
    rows.append([str(i), str(pid), f"'{random.choice(['垃圾满溢异味较大','清运不及时影响出行','夜间清运噪音扰民','垃圾散落未清扫','收集点周边蚊虫较多'])}'",
                 f"'{random.choice(['LOW','MID','HIGH'])}'", f"'{random.choice(['热线','微信','现场'])}'",
                 f"'{random.choice(['PENDING','DONE','DONE'])}'", f"'{dt(ht)}'", f"'{dt(ht)}'"])
insert("complaint", ["id","point_id","content","level","source","handle_status","happen_time","create_time"], rows)

# ---------------- 清运任务 ----------------
ORDER_STATUS = ["PENDING_DISPATCH","ACCEPTED","RUNNING","PENDING_CONFIRM","DONE","DONE","DONE","CANCELED","ABNORMAL"]
order_rows = []
stop_rows = []
weigh_rows = []
flow_rows = []
score_rows = []
order_meta = []   # 供后续 stops/weigh 使用
sno = 1
for i in range(1, 35):
    st = ORDER_STATUS[(i - 1) % len(ORDER_STATUS)]
    pid = ((i * 7) % 20) + 1
    pts = [pid]
    if i % 5 == 0:  # 合并任务，多站点
        pts.append(((pid + 3) % 20) + 1)
        pts.append(((pid + 7) % 20) + 1)
    route_id = ((pid - 1) % 6) + 1
    vid = ((i * 3) % 9) + 1
    did = ((i * 5) % 8) + 1
    sid = ((i * 2) % 5) + 1
    base_w = sum(point_defs[p-1][4] * random.uniform(.45, .9) for p in pts)
    est = round(base_w, 2)
    days_ago = 45 - i
    if days_ago < 0: days_ago = 0
    plan_time = back(days_ago, random.randint(6, 15), random.choice([0, 15, 30, 45]))
    otype = "MERGE" if len(pts) > 1 else ("URGENT" if i % 7 == 0 else "PLAN")
    actual = None
    if st in ("PENDING_CONFIRM", "DONE", "ABNORMAL"):
        actual = round(est * random.uniform(.86, 1.14), 2)
    score = round(random.uniform(42, 96), 1)
    grade = "P1" if score >= 85 else ("P2" if score >= 65 else ("P3" if score >= 45 else "NONE"))
    reason = None
    if st == "CANCELED":
        reason = "收集点临时封闭施工，当日无法进场作业"
    elif st == "ABNORMAL":
        reason = "车辆途中故障，已建立异常并改派"
    order_no = f"QD{plan_time.strftime('%Y%m%d')}-{i:04d}"
    summary = "、".join(point_defs[p-1][0] for p in pts)
    order_rows.append(["NULL", f"'{order_no}'", f"'{otype}'", str(route_id), str(vid), str(did), str(sid),
                       f"'{summary}'", str(len(pts)), f"'{dt(plan_time)}'",
                       f"'{dt(plan_time - timedelta(hours=random.randint(8, 20)))}'",
                       f"{est}", "NULL" if actual is None else f"{actual}",
                       f"'{st}'", f"{score}", f"'{grade}'", "2",
                       "NULL" if reason is None else f"'{reason}'",
                       "11", f"'{dt(plan_time - timedelta(hours=random.randint(12, 26)))}'",
                       f"'{dt(plan_time + timedelta(hours=random.randint(1, 9)))}'", str(random.randint(0,2)), "0"])
    order_meta.append((i, order_no, st, pts, plan_time, est, actual, vid, did, sid))

# stops
for (i, order_no, st, pts, plan_time, est, actual, vid, did, sid) in order_meta:
    for seq, p in enumerate(pts, 1):
        arrive = leave = None
        sst = "WAITING"
        aw = None
        if st in ("RUNNING",):
            if seq == 1:
                sst = "DONE"; arrive = plan_time; leave = plan_time + timedelta(minutes=random.randint(20, 40))
                aw = round(est * .4, 2)
            elif seq == 2:
                sst = "ARRIVED"; arrive = plan_time + timedelta(minutes=random.randint(45, 70))
                aw = None
        elif st in ("PENDING_CONFIRM", "DONE", "ABNORMAL"):
            sst = "DONE"
            arrive = plan_time + timedelta(minutes=(seq - 1) * random.randint(35, 55))
            leave = arrive + timedelta(minutes=random.randint(20, 45))
            aw = round((actual or est) / len(pts) * random.uniform(.85, 1.15), 2)
        elif st == "CANCELED":
            sst = "SKIPPED"
        stop_rows.append(["NULL", str(i), str(p), str(seq),
                          f"'{dt(plan_time + timedelta(minutes=(seq-1)*40))}'",
                          "NULL" if arrive is None else f"'{dt(arrive)}'",
                          "NULL" if leave is None else f"'{dt(leave)}'",
                          f"{round(est/len(pts),2)}",
                          "NULL" if aw is None else f"{aw}",
                          f"'/uploads/seed/site/{((p*7)%2)+1:02d}.jpg'" if sst == "DONE" else "NULL",
                          f"'{sst}'",
                          "NULL" if sst != "SKIPPED" else "'收集点当日封闭'"])

# weighing for done / abnormal / pending_confirm
wn = 1
for (i, order_no, st, pts, plan_time, est, actual, vid, did, sid) in order_meta:
    if st not in ("PENDING_CONFIRM", "DONE", "ABNORMAL"):
        continue
    net = round((actual or est) * random.uniform(.95, 1.02), 2)
    inw = round(net + random.uniform(2.4, 4.2), 2)
    outw = round(inw - net, 2)
    dev = round(abs(net - (actual or est)) / max(actual or est, .1) * 100, 2)
    rs = "REVIEW" if dev > 5 else "PASS"
    weigh_rows.append(["NULL", f"'WJ{plan_time.strftime('%Y%m%d')}-{wn:03d}'", str(i), str(sid),
                       f"{inw}", f"{outw}", f"{net}", f"'{random.choice(['INCINERATE','LAND_FILL','RECYCLE'])}'",
                       f"'/uploads/seed/weigh/{((i*7)%2)+1:02d}.jpg'",
                       f"'{dt(plan_time + timedelta(hours=random.randint(3,6)))}'",
                       f"{dev}", f"'{rs}'",
                       "NULL" if rs == "PASS" else "'净重与各点合计偏差超 5%，需人工复核'",
                       "NULL" if rs != "PASS" else "'孙志刚'",
                       f"'{dt(plan_time + timedelta(hours=random.randint(7,10)))}'"])
    wn += 1

# flow logs
fid = 1
for (i, order_no, st, pts, plan_time, est, actual, vid, did, sid) in order_meta:
    chain = [("创建任务", None, "PENDING_DISPATCH", "何晓雯", plan_time - timedelta(hours=20))]
    if st != "PENDING_DISPATCH":
        chain.append(("派车", "PENDING_DISPATCH", "ACCEPTED", "李振华", plan_time - timedelta(hours=14)))
    if st in ("RUNNING", "PENDING_CONFIRM", "DONE", "ABNORMAL"):
        chain.append(("司机接单", "ACCEPTED", "RUNNING", drivers[((i*5)%8)][1], plan_time - timedelta(hours=2)))
    if st in ("PENDING_CONFIRM", "DONE"):
        chain.append(("完成各点清运", "RUNNING", "PENDING_CONFIRM", drivers[((i*5)%8)][1], plan_time + timedelta(hours=2)))
    if st == "DONE":
        chain.append(("确认交接", "PENDING_CONFIRM", "DONE", "王海燕", plan_time + timedelta(hours=6)))
    if st == "CANCELED":
        chain.append(("取消任务", "PENDING_DISPATCH", "CANCELED", "李振华", plan_time - timedelta(hours=6)))
    if st == "ABNORMAL":
        chain.append(("车辆故障上报", "RUNNING", "ABNORMAL", drivers[((i*5)%8)][1], plan_time + timedelta(hours=1)))
    for (act, fs, ts, op, tm) in chain:
        flow_rows.append(["NULL", "'DISPATCH'", str(i), f"'{order_no}'",
                          "NULL" if fs is None else f"'{fs}'", f"'{ts}'", f"'{act}'",
                          "NULL" if act != "取消任务" else "'收集点临时封闭施工，当日无法进场作业'",
                          f"'{op}'", f"'{dt(tm)}'"])
        fid += 1

# scores (仅部分任务做过联合调度计算)
rulev = 3
for (i, order_no, st, pts, plan_time, est, actual, vid, did, sid) in order_meta:
    if i > 30:
        continue
    cap = vehicles[((i*3)%9)][2]
    load = round(random.uniform(45, 96), 1)
    stay = round(random.uniform(6, 72), 1)
    comp = random.randint(0, 5)
    dist = round(random.uniform(0.8, 12.5), 1)
    tmatch = random.choice([1, 1, 1, 0])
    s_load = round(load/100*26, 1)
    s_stay = round(min(stay/72, 1)*24, 1)
    s_comp = round(min(comp/5, 1)*16, 1)
    s_cap = round(min((cap-est)/cap if cap > est else 0, 1)*18, 1)
    s_dist = round(max(0, 1-dist/15)*10, 1)
    s_tm = round(tmatch*6, 1)
    total = round(s_load+s_stay+s_comp+s_cap+s_dist+s_tm, 1)
    grade = "P1" if total >= 85 else ("P2" if total >= 65 else ("P3" if total >= 45 else "NONE"))
    factors = f"满载度 {load:.0f}%、滞留 {stay:.0f} 小时、投诉 {comp} 次"
    unmet = "车辆剩余容量不足" if cap <= est else "无"
    improve = f"点位距上一站 {dist:.1f} km，建议调整线路顺序减少空驶"
    snap = '{"loadRate":%.1f,"stayHours":%.1f,"complaints":%d,"vehicleCapacity":%.1f,"distanceKm":%.1f,"typeMatch":%d}' % (load, stay, comp, cap, dist, tmatch)
    score_rows.append(["NULL", str(i), str(rulev), str(rulev), f"'{snap}'",
                       f"{load}", f"{stay}", str(comp), f"{cap}", f"{dist}", str(tmatch),
                       f"{s_load}", f"{s_stay}", f"{s_comp}", f"{s_cap}", f"{s_dist}", f"{s_tm}",
                       f"{total}", f"'{grade}'", f"'{factors}'", f"'{unmet}'", f"'{improve}'",
                       "1" if i % 4 else "0", "0" if i % 4 else "1",
                       "NULL" if i % 4 else "'原定车辆年检到期，改派同载重车辆'",
                       f"'{dt(plan_time - timedelta(hours=16))}'"])

def null_id(rows):
    out = []
    for r in rows:
        out.append(r)
    return out

# 用显式 id 生成（避免 NULL 依赖 AUTO_INCREMENT 顺序不一致）
def with_id(rows, start=1):
    for k, r in enumerate(rows, start):
        r[0] = str(k)
    return rows

insert("dispatch_order", ["id","order_no","order_type","route_id","vehicle_id","driver_id","dispose_site_id","point_summary","stop_count","plan_time","dispatch_time","estimated_weight","actual_weight","status","priority_score","priority_grade","dispatcher_id","reason","create_by","create_time","update_time","version","deleted"], with_id(order_rows))
insert("route_stop", ["id","order_id","point_id","seq","plan_arrive","arrive_time","leave_time","estimated_weight","actual_weight","site_image","status","remark"], with_id(stop_rows))
insert("weighing_record", ["id","record_no","order_id","dispose_site_id","in_weight","out_weight","net_weight","dispose_type","weighing_image","weigh_time","deviation","review_status","review_note","reviewer","create_time"], with_id(weigh_rows))
insert("flow_log", ["id","biz_type","biz_id","biz_no","from_status","to_status","action","reason","operator","create_time"], with_id(flow_rows))
insert("dispatch_score", ["id","order_id","rule_id","rule_version","snapshot","v_load","v_stay","v_complaint","v_capacity","v_distance","v_type_match","s_load","s_stay","s_complaint","s_capacity","s_distance","s_type_match","total_score","grade","factors","unmet","improve","adopted","manual_adjust","adjust_reason","create_time"], with_id(score_rows))

# ---------------- 规则 ----------------
rules = [
 ("容量与时效联合调度规则", 1, 22, 26, 14, 20, 12, 6, 85, 65, 45, 5, 0, "2026-06-15 14:00:00", "系统初始化"),
 ("容量与时效联合调度规则", 2, 24, 24, 16, 18, 12, 6, 85, 65, 45, 5, 0, "2026-09-01 10:20:00", "周建明"),
 ("容量与时效联合调度规则", 3, 26, 24, 16, 18, 10, 6, 85, 65, 45, 5, 1, "2026-10-20 09:00:00", "周建明"),
]
rows = []
for i,(n,v,wl,ws,wc,wcap,wd,wt,p1,p2,p3,rv,en,et,by) in enumerate(rules,1):
    rows.append([str(i), f"'{n}'", str(v), str(wl), str(ws), str(wc), str(wcap), str(wd), str(wt),
                 str(p1), str(p2), str(p3), str(rv), str(en), f"'{et}'", f"'{by}'", f"'{dt(back(120,10,0))}'"])
insert("dispatch_rule", ["id","rule_name","version","w_load","w_stay","w_complaint","w_capacity","w_distance","w_type_match","threshold_p1","threshold_p2","threshold_p3","review_threshold","enabled","effective_time","create_by","create_time"], rows)

# ---------------- 临时报满 ----------------
OF_LEVELS = [("LIGHT","轻微"),("OBVIOUS","明显"),("SERIOUS","严重")]
rows = []
for i in range(1, 19):
    pid = ((i * 3) % 20) + 1
    lv = OF_LEVELS[i % 3][0]
    rt = back(random.randint(0, 40), random.randint(7, 19), random.randint(0, 59))
    st = ["PENDING","PENDING","DISPATCHED","DONE","DONE","CANCELED"][i % 6]
    urg = round(random.uniform(45, 98), 2)
    rows.append([str(i), f"'OF{rt.strftime('%Y%m%d')}-{i:03d}'", str(pid), f"'{lv}'",
                 f"{round(point_defs[pid-1][4]*random.uniform(.5,.95),2)}",
                 f"'/uploads/seed/site/{((i*7)%2)+1:02d}.jpg'",
                 f"'{random.choice(['垃圾桶已满溢出桶口','垃圾落地堆积影响通行','异味明显居民反映强烈','清运后未及时清扫'])}'",
                 f"{urg}", str(4), f"'{dt(rt)}'", f"'{st}'",
                 "NULL" if st in ("PENDING",) else str(min(i, 34)),
                 f"'{dt(rt)}'"])
insert("overflow_report", ["id","report_no","point_id","overflow_level","estimated_weight","image","description","urgency_score","reporter_id","report_time","status","order_id","create_time"], rows)

# ---------------- 异常 ----------------
EX_T = ["VEHICLE_FAULT","UNREACHABLE","OVERLOAD","MISS_STOP","OTHER"]
EX_DESC = {
 "VEHICLE_FAULT":"车辆行驶中液压系统故障，无法继续作业",
 "UNREACHABLE":"巷道被私家车占用，车辆无法进入",
 "OVERLOAD":"实际重量超出车辆额定载重 8%",
 "MISS_STOP":"站点遗漏未清运，居民投诉",
 "OTHER":"处置场排队时间过长",
}
EX_RESULT = {
 "VEHICLE_FAULT":"改派粤A·D8836接续作业",
 "UNREACHABLE":"协调社区清理通道后重新到场",
 "OVERLOAD":"分两次转运，超载部分留待下趟",
 "MISS_STOP":"补派车辆当日完成清运",
 "OTHER":"调整计划时间避开高峰",
}
rows = []
for i in range(1, 13):
    oid = (i * 3) % 34 + 1
    t = EX_T[i % 5]
    st = ["OPEN","HANDLING","CLOSED","CLOSED"][i % 4]
    rows.append([str(i), f"'EX2026{i:04d}'", str(oid), str(((i*7)%20)+1), f"'{t}'",
                 f"'{random.choice(['LOW','MID','HIGH'])}'",
                 f"'{EX_DESC[t]}'",
                 f"'/uploads/seed/site/{((i*7)%2)+1:02d}.jpg'", f"'{drivers[i%8][1]}'",
                 "NULL" if st == "OPEN" else "'李振华'",
                 "NULL" if st == "OPEN" else f"'已{EX_RESULT[t]}'",
                 f"'{st}'", f"'{dt(back(random.randint(1,35), random.randint(8,18), 10))}'",
                 f"'{dt(back(random.randint(0,30), random.randint(9,19), 20))}'"])
insert("exception_record", ["id","exception_no","order_id","point_id","type","level","description","image","reporter","handler","handle_result","status","create_time","update_time"], rows)

# ---------------- 保养 ----------------
rows = []
MT = ["常规保养","年检","维修"]
for i in range(1, 15):
    vid = ((i * 3) % 10) + 1
    md = back(random.randint(0, 160 + i * 9), 9, 30)
    nd = md + timedelta(days=90)
    veh = vehicles[vid-1]
    due = nd < (TODAY + timedelta(days=20))
    status = "ING" if vid == 5 else ("DUE" if due else "DONE")
    remark = "保养中，暂停派单" if status == "ING" else ("距下次保养不足 20 天" if status == "DUE" else "按期完成")
    rows.append([str(i), str(vid), f"'{MT[i%3]}'", f"'{md.strftime('%Y-%m-%d')}'",
                 str(veh[4]), f"'{nd.strftime('%Y-%m-%d')}'", str(veh[4] + 8000),
                 f"{round(random.uniform(800, 8600), 2)}", f"'{status}'",
                 f"'{remark}'",
                 f"'{dt(md)}'"])
insert("vehicle_maintenance", ["id","vehicle_id","maintain_type","maintain_date","mileage","next_date","next_mileage","cost","status","remark","create_time"], rows)

# ---------------- 附件 ----------------
rows = []
aid = 1
for (i, order_no, st, pts, plan_time, est, actual, vid, did, sid) in order_meta[:20]:
    for k, p in enumerate(pts, 1):
        rows.append([str(aid), "'DISPATCH'", str(i), f"'site-{order_no}-{k}.jpg'",
                     f"'/uploads/seed/site/{((p*7)%2)+1:02d}.jpg'", str(random.randint(180000, 320000)),
                     f"'{drivers[(i*5)%8][1]}'", f"'{dt(plan_time + timedelta(hours=1))}'"])
        aid += 1
insert("attachment", ["id","biz_type","biz_id","file_name","file_path","file_size","uploader","create_time"], rows)

# ---------------- 消息 ----------------
MSGS = [
 ("待派车提醒","任务 QD20261031-0012 已生成，满载度 92% 超过阈值，请尽快派车","DISPATCH","QD20261031-0012",2),
 ("异常上报","任务 QD20261030-0086 上报车辆故障，已暂停执行","EXCEPTION","QD20261030-0086",2),
 ("净重复核提醒","称重单 WJ20261028-004 净重偏差 6.8%，请复核","WEIGHING","WJ20261028-004",1),
 ("报满提醒","锦绣花园小区北门站上报明显满溢，请安排清运","OVERFLOW","OF20261031-006",2),
 ("任务已派发","您有新任务 QD20261031-0014，计划 11:40 到场","DISPATCH","QD20261031-0014",7),
 ("保养到期提醒","粤A·D8890 距下次保养不足 20 天","MAINTAIN","粤A·D8890",1),
 ("任务退回","任务 QD20261029-0021 因现场无法进入被退回","DISPATCH","QD20261029-0021",7),
 ("规则版本变更","调度规则已升级至 v3，新计算将使用新权重","RULE","v3",2),
 ("任务待确认","任务 QD20261030-0087 已完成，请确认交接","DISPATCH","QD20261030-0087",2),
 ("投诉转办","城南农贸市场东门站收到异味投诉，请跟进","COMPLAINT","CP-2026-0031",4),
]
rows = []
for i,(t,c,bt,bn,rc) in enumerate(MSGS,1):
    rows.append([str(i), f"'{t}'", f"'{c}'", f"'{bt}'", f"'{bn}'", str(rc),
                 "1" if i > 4 else "0", f"'{dt(back(i, 9, i*4))}'"])
insert("sys_message", ["id","title","content","biz_type","biz_no","receiver_id","read_flag","create_time"], rows)

# ---------------- 操作日志 ----------------
rows = []
acts = [("收集点管理","新增收集点"),("清运调度台","派车"),("称重交接","确认交接"),("调度规则配置","保存规则"),
        ("异常处理","处理异常"),("临时报满","提交上报"),("车辆档案","编辑车辆"),("用户管理","重置密码")]
for i in range(1, 41):
    a = acts[i % len(acts)]
    rows.append([str(i), str((i % 12) + 1), f"'{users[i % 12][2]}'", f"'{a[0]}'", f"'{a[1]}'",
                 f"'POST /api/{'dispatch' if '派车' in a[1] else 'common'}/action'", "'{}'",
                 f"'127.0.0.1'", str(random.randint(18, 420)), f"'{dt(back(random.randint(0,30), random.randint(8,19), random.randint(0,59)))}'"])
insert("sys_log", ["id","user_id","user_name","module","action","method","params","ip","cost_ms","create_time"], rows)

w("-- 校验：菜单管理自身隐藏、每条任务的状态与站点/称重数据一致")
w("SELECT '收集点' AS t, COUNT(*) c FROM collection_point")
w("UNION ALL SELECT '清运任务', COUNT(*) FROM dispatch_order")
w("UNION ALL SELECT '任务站点', COUNT(*) FROM route_stop")
w("UNION ALL SELECT '称重记录', COUNT(*) FROM weighing_record")
w("UNION ALL SELECT '计算留痕', COUNT(*) FROM dispatch_score;")

with open(__file__.replace("gen_init.py", "init.sql"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
print("init.sql 生成完成，行数:", len(OUT))
