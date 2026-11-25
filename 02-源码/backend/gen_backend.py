#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 MySQL 真实表结构反向生成 entity / mapper 与工程骨架文件（NEW-013）。"""
import os, subprocess, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "backend/src/main/java/com/grad/waste")
RES = os.path.join(BASE, "backend/src/main/resources")
PKG = "com.grad.waste"

# 表 -> (实体名, 说明)
TABLES = {
 "sys_org": ("SysOrg", "责任单位"),
 "sys_role": ("SysRole", "角色"),
 "sys_menu": ("SysMenu", "菜单"),
 "sys_role_menu": ("SysRoleMenu", "角色菜单"),
 "sys_user": ("SysUser", "用户"),
 "sys_dict": ("SysDict", "字典"),
 "sys_message": ("SysMessage", "站内消息"),
 "sys_log": ("SysLog", "操作日志"),
 "dispose_site": ("DisposeSite", "处置场"),
 "route": ("CleanRoute", "清运线路"),
 "collection_point": ("CollectionPoint", "垃圾收集点"),
 "vehicle": ("Vehicle", "清运车辆"),
 "driver": ("Driver", "司机档案"),
 "collection_plan": ("CollectionPlan", "周期清运计划"),
 "overflow_report": ("OverflowReport", "临时报满"),
 "complaint": ("Complaint", "投诉记录"),
 "dispatch_order": ("DispatchOrder", "清运任务"),
 "route_stop": ("RouteStop", "任务站点"),
 "weighing_record": ("WeighingRecord", "处置称重交接"),
 "exception_record": ("ExceptionRecord", "异常记录"),
 "vehicle_maintenance": ("VehicleMaintenance", "车辆保养"),
 "attachment": ("Attachment", "附件"),
 "flow_log": ("FlowLog", "业务流转日志"),
 "dispatch_rule": ("DispatchRule", "调度规则版本"),
 "dispatch_score": ("DispatchScore", "调度计算留痕"),
}

def q(sql):
    out = subprocess.run(["/opt/homebrew/bin/mysql","-uroot","-p123456","new_013","-N","-B","-e",sql],
                         capture_output=True, text=True)
    rows = []
    for line in out.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        parts += [""] * (6 - len(parts))
        rows.append(parts[:6])
    return rows

def camel(s):
    parts = s.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])

TYPE_MAP = {
 "bigint": "Long", "int": "Integer", "tinyint": "Integer", "smallint": "Integer",
 "decimal": "BigDecimal", "varchar": "String", "char": "String", "text": "String",
 "datetime": "LocalDateTime", "date": "LocalDate", "timestamp": "LocalDateTime",
 "double": "Double", "float": "Float",
}

def gen_entity(table, cls, desc):
    cols = q(f"SELECT column_name, data_type, is_nullable, column_comment, column_key, extra "
             f"FROM information_schema.columns WHERE table_schema='new_013' AND table_name='{table}' "
             f"ORDER BY ordinal_position")
    imports = set()
    fields, getset = [], []
    for (name, dtype, nullable, comment, key, extra) in cols:
        jt = TYPE_MAP.get(dtype, "String")
        if jt == "BigDecimal": imports.add("java.math.BigDecimal")
        if jt == "LocalDateTime": imports.add("java.time.LocalDateTime")
        if jt == "LocalDate": imports.add("java.time.LocalDate")
        fname = camel(name)
        ann = ""
        if key == "PRI":
            ann = '    @TableId(type = IdType.AUTO)\n'
        if name == "deleted":
            ann = '    @TableLogic\n'
        fields.append(f"{ann}    /** {comment} */\n    private {jt} {fname};\n")
    body = "\n".join(fields)
    src = f"""package {PKG}.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
{chr(10).join('import ' + i + ';' for i in sorted(imports))}

/**
 * {desc}（表 {table}）
 */
@Data
@TableName("{table}")
public class {cls} {{

{body}}}
"""
    return src

def gen_mapper(cls, desc):
    return f"""package {PKG}.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import {PKG}.entity.{cls};
import org.apache.ibatis.annotations.Mapper;

/** {desc} Mapper */
@Mapper
public interface {cls}Mapper extends BaseMapper<{cls}> {{
}}
"""

os.makedirs(os.path.join(SRC, "entity"), exist_ok=True)
os.makedirs(os.path.join(SRC, "mapper"), exist_ok=True)

for table, (cls, desc) in TABLES.items():
    with open(os.path.join(SRC, "entity", cls + ".java"), "w", encoding="utf-8") as f:
        f.write(gen_entity(table, cls, desc))
    with open(os.path.join(SRC, "mapper", cls + "Mapper.java"), "w", encoding="utf-8") as f:
        f.write(gen_mapper(cls, desc))
print("实体/Mapper 生成完成:", len(TABLES))
