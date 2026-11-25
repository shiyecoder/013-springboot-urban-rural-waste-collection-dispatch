#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 NEW-013 控制器层：通用 CRUD + 核心业务控制器。"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "backend/src/main/java/com/grad/waste")
PKG = "com.grad.waste"
FILES = {}

def crud(cls, entity, path, label, keyword_cols, order_col="id", status_col=None, extra_imports=""):
    """标准 CRUD 控制器：服务端分页 + 关键词搜索 + 状态筛选 + 增删改查 + 下拉选项"""
    kw = "\n".join([f'                w.and(x -> x.like("{c}", kw)' + "".join(
        [f'.or().like("{k}", kw)' for k in keyword_cols[i+1:]]) + ");" for i, c in enumerate(keyword_cols[:1])])
    kw_lines = ""
    if keyword_cols:
        expr = ".or().like(\""+ "\", kw).or().like(\"".join([""])
        parts = []
        for c in keyword_cols:
            parts.append(f'w.like("{c}", kw)')
        kw_lines = "            if (kw != null && !kw.isBlank()) {\n                w.and(x -> " + \
                   ".or().".join([f'like("{c}", kw)' for c in keyword_cols]) + ");\n            }"
    status_line = ""
    if status_col:
        status_line = f'            if (status != null && !status.isBlank()) w.eq("{status_col}", status);'
    return f"""package {PKG}.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.{entity};
import com.grad.waste.mapper.{entity}Mapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * {label}管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/{path}")
public class {cls} {{

    private final {entity}Mapper mapper;

    public {cls}({entity}Mapper mapper) {{
        this.mapper = mapper;
    }}

    @GetMapping("/page")
    public R<PageResult<{entity}>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {{
        QueryWrapper<{entity}> w = new QueryWrapper<>();
{kw_lines}
{status_line}
        w.orderByDesc("{order_col}");
        Page<{entity}> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }}

    @GetMapping("/options")
    public R<List<{entity}>> options() {{
        return R.ok(mapper.selectList(new QueryWrapper<{entity}>().orderByAsc("{order_col}")));
    }}

    @GetMapping("/{{id}}")
    public R<{entity}> get(@PathVariable Long id) {{
        {entity} o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }}

    @PostMapping
    public R<{entity}> add(@RequestBody {entity} o) {{
        mapper.insert(o);
        return R.ok(o);
    }}

    @PutMapping("/{{id}}")
    public R<{entity}> update(@PathVariable Long id, @RequestBody {entity} o) {{
        if (mapper.selectById(id) == null) throw new BizException("记录不存在或已删除");
        mapper.updateById(o);
        return R.ok(o);
    }}

    @DeleteMapping("/{{id}}")
    public R<Void> delete(@PathVariable Long id) {{
        mapper.deleteById(id);
        return R.ok();
    }}
}}
"""

MODULES = [
    ("VehicleController", "Vehicle", "vehicle", "车辆档案", ["plate_no", "vehicle_type"], "id", "status"),
    ("DriverController", "Driver", "driver", "司机档案", ["name", "phone", "driver_no"], "id", "status"),
    ("RouteController", "CleanRoute", "route", "清运线路", ["route_name", "route_code"], "id", "status"),
    ("SiteController", "DisposeSite", "site", "处置场", ["site_name", "site_code"], "id", "status"),
    ("PlanController", "CollectionPlan", "plan", "周期计划", ["plan_code"], "id", "status"),
    ("ComplaintController", "Complaint", "complaint", "投诉记录", ["content"], "id", "handle_status"),
    ("MaintenanceController", "VehicleMaintenance", "maintenance", "车辆保养", ["maintain_type"], "id", "status"),
    ("OverflowController", "OverflowReport", "overflow", "临时报满", ["report_no"], "id", "status"),
    ("WeighingController", "WeighingRecord", "weighing", "称重交接", ["record_no"], "id", "review_status"),
    ("ExceptionController", "ExceptionRecord", "exception", "异常记录", ["exception_no", "description"], "id", "status"),
    ("UserController", "SysUser", "user", "用户", ["username", "real_name"], "id", "status"),
    ("RoleController", "SysRole", "role", "角色", ["role_name", "role_code"], "id", None),
    ("MenuController", "SysMenu", "menu", "菜单", ["menu_name"], "sort", None),
    ("MessageController", "SysMessage", "message", "站内消息", ["title"], "id", None),
    ("RuleController", "DispatchRule", "rule", "调度规则", ["rule_name"], "id", None),
]
for cls, entity, path, label, cols, order_col, status_col in MODULES:
    FILES[f"{SRC}/controller/{cls}.java"] = crud(cls, entity, path, label, cols, order_col, status_col)

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
print("生成", len(FILES), "个 CRUD 控制器")
