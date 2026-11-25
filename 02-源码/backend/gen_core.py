#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 NEW-013 核心业务控制器（认证 / 收集点 / 调度 / 报表 / 文件 / 评分）。"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "backend/src/main/java/com/grad/waste")
PKG = "com.grad.waste"
FILES = {}

FILES[f"{SRC}/controller/AuthController.java"] = f"""package {PKG}.controller;

import com.grad.waste.common.R;
import com.grad.waste.service.AuthService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 认证：登录、当前用户、动态菜单、资料与密码 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {{

    private final AuthService authService;

    public AuthController(AuthService authService) {{
        this.authService = authService;
    }}

    @PostMapping("/login")
    public R<Map<String, Object>> login(@RequestBody Map<String, String> body) {{
        return R.ok(authService.login(body.get("username"), body.get("password")));
    }}

    @GetMapping("/me")
    public R<Map<String, Object>> me() {{
        return R.ok(authService.me());
    }}

    @GetMapping("/menus")
    public R<Object> menus() {{
        return R.ok(authService.me().get("menus"));
    }}

    @PutMapping("/profile")
    public R<Void> profile(@RequestBody Map<String, String> body) {{
        authService.updateProfile(body.get("realName"), body.get("phone"), body.get("email"), body.get("avatar"));
        return R.ok();
    }}

    @PostMapping("/password")
    public R<Void> password(@RequestBody Map<String, String> body) {{
        authService.changePassword(body.get("oldPassword"), body.get("newPassword"));
        return R.ok();
    }}
}}
"""

FILES[f"{SRC}/controller/PointController.java"] = f"""package {PKG}.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.*;
import com.grad.waste.mapper.*;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/** 收集点档案：分页、详情、增改删、下拉、区域汇总 */
@RestController
@RequestMapping("/api/point")
public class PointController {{

    private final CollectionPointMapper mapper;
    private final CollectionPlanMapper planMapper;
    private final RouteStopMapper stopMapper;

    public PointController(CollectionPointMapper mapper, CollectionPlanMapper planMapper, RouteStopMapper stopMapper) {{
        this.mapper = mapper;
        this.planMapper = planMapper;
        this.stopMapper = stopMapper;
    }}

    @GetMapping("/page")
    public R<PageResult<CollectionPoint>> page(@RequestParam(defaultValue = "1") long page,
                                               @RequestParam(defaultValue = "10") long size,
                                               @RequestParam(required = false) String kw,
                                               @RequestParam(required = false) String area,
                                               @RequestParam(required = false) String wasteType,
                                               @RequestParam(required = false) String status,
                                               @RequestParam(required = false) Integer loadMin,
                                               @RequestParam(required = false) Integer loadMax) {{
        LambdaQueryWrapper<CollectionPoint> w = new LambdaQueryWrapper<>();
        if (kw != null && !kw.isBlank()) {{
            w.and(x -> x.like(CollectionPoint::getPointName, kw).or().like(CollectionPoint::getPointCode, kw));
        }}
        if (area != null && !area.isBlank()) w.eq(CollectionPoint::getArea, area);
        if (wasteType != null && !wasteType.isBlank()) w.eq(CollectionPoint::getWasteType, wasteType);
        if (status != null && !status.isBlank()) w.eq(CollectionPoint::getStatus, status);
        if (loadMin != null) w.ge(CollectionPoint::getLoadRate, loadMin);
        if (loadMax != null) w.le(CollectionPoint::getLoadRate, loadMax);
        w.orderByDesc(CollectionPoint::getLoadRate).orderByDesc(CollectionPoint::getUpdateTime);
        Page<CollectionPoint> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }}

    @GetMapping("/options")
    public R<List<CollectionPoint>> options() {{
        return R.ok(mapper.selectList(new LambdaQueryWrapper<CollectionPoint>()
                .eq(CollectionPoint::getStatus, "NORMAL")
                .or().eq(CollectionPoint::getStatus, "OVERFLOW")
                .orderByAsc(CollectionPoint::getPointCode)));
    }}

    @GetMapping("/areas")
    public R<List<String>> areas() {{
        List<String> areas = new ArrayList<>();
        mapper.selectList(null).forEach(p -> {{ if (!areas.contains(p.getArea())) areas.add(p.getArea()); }});
        return R.ok(areas);
    }}

    @GetMapping("/{{id}}")
    public R<CollectionPoint> get(@PathVariable Long id) {{
        CollectionPoint p = mapper.selectById(id);
        if (p == null) throw new BizException("收集点不存在或已删除");
        return R.ok(p);
    }}

    @PostMapping
    public R<CollectionPoint> add(@RequestBody CollectionPoint p) {{
        validate(p, null);
        // 满载度由后端计算，前端传值不采信
        p.setLoadRate(calcRate(p));
        if (p.getStatus() == null) p.setStatus("NORMAL");
        mapper.insert(p);
        return R.ok(p);
    }}

    @PutMapping("/{{id}}")
    public R<CollectionPoint> update(@PathVariable Long id, @RequestBody CollectionPoint p) {{
        CollectionPoint old = mapper.selectById(id);
        if (old == null) throw new BizException("收集点不存在或已删除");
        if (p.getVersion() != null && old.getVersion() != null && !p.getVersion().equals(old.getVersion())) {{
            throw new BizException("该记录已被他人更新，请刷新后重试");
        }}
        p.setId(id);
        p.setPointCode(old.getPointCode());
        p.setLoadRate(calcRate(p));
        p.setVersion((old.getVersion() == null ? 0 : old.getVersion()) + 1);
        mapper.updateById(p);
        return R.ok(p);
    }}

    @DeleteMapping("/{{id}}")
    public R<Void> delete(@PathVariable Long id) {{
        Long plans = planMapper.selectCount(new LambdaQueryWrapper<CollectionPlan>().eq(CollectionPlan::getPointId, id));
        if (plans > 0) throw new BizException("该收集点已被周期计划引用，不能删除，请先停用");
        mapper.deleteById(id);
        return R.ok();
    }}

    private void validate(CollectionPoint p, Long id) {{
        if (p.getPointCode() == null || p.getPointCode().isBlank()) throw new BizException("点位编码必填");
        p.setPointCode(p.getPointCode().trim());
        if (p.getPointCode().length() > 50) throw new BizException("点位编码长度不能超过 50 个字符");
        if (p.getPointName() == null || p.getPointName().isBlank()) throw new BizException("点位名称必填");
        if (p.getArea() == null || p.getArea().isBlank()) throw new BizException("所属区域必填");
        if (p.getCapacity() == null || p.getCapacity().doubleValue() < 0) throw new BizException("容量不得为负数");
        Long dup = mapper.selectCount(new LambdaQueryWrapper<CollectionPoint>()
                .eq(CollectionPoint::getPointCode, p.getPointCode())
                .ne(id != null, CollectionPoint::getId, id));
        if (dup > 0) throw new BizException("点位编码已存在，请更换");
    }}

    private Integer calcRate(CollectionPoint p) {{
        if (p.getCapacity() == null || p.getCapacity().doubleValue() <= 0) return 0;
        double load = p.getCurrentLoad() == null ? 0 : p.getCurrentLoad().doubleValue();
        return (int) Math.min(100, Math.round(load / p.getCapacity().doubleValue() * 100));
    }}
}}
"""

FILES[f"{SRC}/controller/DispatchController.java"] = f"""package {PKG}.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.DispatchOrder;
import com.grad.waste.entity.DispatchScore;
import com.grad.waste.mapper.DispatchOrderMapper;
import com.grad.waste.mapper.DispatchScoreMapper;
import com.grad.waste.service.DispatchService;
import com.grad.waste.service.ScoreService;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 清运调度：分页、详情、派车/改派、状态流转、联合调度计算、人工调整。
 */
@RestController
@RequestMapping("/api/dispatch")
public class DispatchController {{

    private final DispatchOrderMapper orderMapper;
    private final DispatchScoreMapper scoreMapper;
    private final DispatchService dispatchService;
    private final ScoreService scoreService;

    public DispatchController(DispatchOrderMapper orderMapper, DispatchScoreMapper scoreMapper,
                              DispatchService dispatchService, ScoreService scoreService) {{
        this.orderMapper = orderMapper;
        this.scoreMapper = scoreMapper;
        this.dispatchService = dispatchService;
        this.scoreService = scoreService;
    }}

    @GetMapping("/page")
    public R<PageResult<DispatchOrder>> page(@RequestParam(defaultValue = "1") long page,
                                             @RequestParam(defaultValue = "10") long size,
                                             @RequestParam(required = false) String kw,
                                             @RequestParam(required = false) String status,
                                             @RequestParam(required = false) String date) {{
        LambdaQueryWrapper<DispatchOrder> w = new LambdaQueryWrapper<>();
        if (kw != null && !kw.isBlank()) {{
            w.and(x -> x.like(DispatchOrder::getOrderNo, kw).or().like(DispatchOrder::getPointSummary, kw));
        }}
        if (status != null && !status.isBlank()) w.eq(DispatchOrder::getStatus, status);
        if (date != null && !date.isBlank()) {{
            LocalDateTime d0 = LocalDateTime.parse(date + " 00:00:00", DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
            w.ge(DispatchOrder::getPlanTime, d0).lt(DispatchOrder::getPlanTime, d0.plusDays(1));
        }}
        // 待本人处理优先、更新时间倒序
        w.orderByAsc(DispatchOrder::getStatus).orderByDesc(DispatchOrder::getUpdateTime);
        Page<DispatchOrder> p = orderMapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }}

    @GetMapping("/{{id}}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {{
        return R.ok(dispatchService.detail(id));
    }}

    @PostMapping("/{{id}}/assign")
    public R<Void> assign(@PathVariable Long id, @RequestBody Map<String, Object> body) {{
        Long vehicleId = body.get("vehicleId") == null ? null : Long.valueOf(String.valueOf(body.get("vehicleId")));
        Long driverId = body.get("driverId") == null ? null : Long.valueOf(String.valueOf(body.get("driverId")));
        Long siteId = body.get("disposeSiteId") == null ? null : Long.valueOf(String.valueOf(body.get("disposeSiteId")));
        LocalDateTime planTime = null;
        if (body.get("planTime") != null) {{
            String s = String.valueOf(body.get("planTime")).replace("T", " ");
            if (s.length() == 16) s = s + ":00";
            planTime = LocalDateTime.parse(s, DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        }}
        dispatchService.assign(id, vehicleId, driverId, siteId, planTime, false, null);
        return R.ok();
    }}

    @PostMapping("/{{id}}/reassign")
    public R<Void> reassign(@PathVariable Long id, @RequestBody Map<String, Object> body) {{
        Long vehicleId = Long.valueOf(String.valueOf(body.get("vehicleId")));
        Long driverId = Long.valueOf(String.valueOf(body.get("driverId")));
        Long siteId = body.get("disposeSiteId") == null ? null : Long.valueOf(String.valueOf(body.get("disposeSiteId")));
        dispatchService.assign(id, vehicleId, driverId, siteId, null, true, String.valueOf(body.get("reason")));
        return R.ok();
    }}

    @PostMapping("/{{id}}/transition")
    public R<Void> transition(@PathVariable Long id, @RequestBody Map<String, String> body) {{
        dispatchService.transition(id, body.get("action"), body.get("reason"));
        return R.ok();
    }}

    /** 执行「容量与时效联合调度」并返回明细依据，同时写留痕 */
    @PostMapping("/{{id}}/evaluate")
    public R<DispatchScore> evaluate(@PathVariable Long id) {{
        DispatchOrder o = orderMapper.selectById(id);
        return R.ok(scoreService.evaluate(o, true));
    }}

    @PostMapping("/{{id}}/adjust")
    public R<Void> adjust(@PathVariable Long id, @RequestBody Map<String, Object> body) {{
        Long vehicleId = body.get("vehicleId") == null ? null : Long.valueOf(String.valueOf(body.get("vehicleId")));
        dispatchService.adjust(id, String.valueOf(body.get("reason")), vehicleId);
        return R.ok();
    }}

    @GetMapping("/{{id}}/scores")
    public R<List<DispatchScore>> scores(@PathVariable Long id) {{
        return R.ok(scoreMapper.selectList(new LambdaQueryWrapper<DispatchScore>()
                .eq(DispatchScore::getOrderId, id).orderByDesc(DispatchScore::getId)));
    }}
}}
"""

FILES[f"{SRC}/controller/ScoreController.java"] = f"""package {PKG}.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.DispatchScore;
import com.grad.waste.mapper.DispatchScoreMapper;
import org.springframework.web.bind.annotation.*;

/** 调度计算留痕查询：可按等级与任务过滤 */
@RestController
@RequestMapping("/api/score")
public class ScoreController {{

    private final DispatchScoreMapper mapper;

    public ScoreController(DispatchScoreMapper mapper) {{
        this.mapper = mapper;
    }}

    @GetMapping("/page")
    public R<PageResult<DispatchScore>> page(@RequestParam(defaultValue = "1") long page,
                                             @RequestParam(defaultValue = "10") long size,
                                             @RequestParam(required = false) String grade,
                                             @RequestParam(required = false) Long orderId) {{
        LambdaQueryWrapper<DispatchScore> w = new LambdaQueryWrapper<>();
        if (grade != null && !grade.isBlank()) w.eq(DispatchScore::getGrade, grade);
        if (orderId != null) w.eq(DispatchScore::getOrderId, orderId);
        w.orderByDesc(DispatchScore::getId);
        Page<DispatchScore> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }}

    /** 采纳率 / 人工调整率，用于验证创新模块有效性 */
    @GetMapping("/effect")
    public R<java.util.Map<String, Object>> effect() {{
        long total = mapper.selectCount(null);
        long adopted = mapper.selectCount(new LambdaQueryWrapper<DispatchScore>().eq(DispatchScore::getAdopted, 1));
        long manual = mapper.selectCount(new LambdaQueryWrapper<DispatchScore>().eq(DispatchScore::getManualAdjust, 1));
        java.util.Map<String, Object> m = new java.util.LinkedHashMap<>();
        m.put("total", total);
        m.put("adopted", adopted);
        m.put("manual", manual);
        m.put("adoptRate", total == 0 ? 0 : Math.round(adopted * 1000.0 / total) / 10.0);
        m.put("manualRate", total == 0 ? 0 : Math.round(manual * 1000.0 / total) / 10.0);
        return R.ok(m);
    }}
}}
"""

FILES[f"{SRC}/controller/FileController.java"] = f"""package {PKG}.controller;

import com.grad.waste.common.BizException;
import com.grad.waste.common.R;
import com.grad.waste.common.UserContext;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 文件上传：保存到项目根目录 uploads/yyyyMM/，返回相对路径 /uploads/**。
 * 只允许图片与 PDF，禁止外部 URL。
 */
@RestController
@RequestMapping("/api/file")
public class FileController {{

    private static final Set<String> ALLOW = Set.of("jpg", "jpeg", "png", "webp", "pdf");

    @Value("${{app.upload-dir:./uploads}}")
    private String uploadDir;

    @PostMapping("/upload")
    public R<Map<String, Object>> upload(@RequestParam("file") MultipartFile file) throws Exception {{
        if (file == null || file.isEmpty()) throw new BizException("请选择文件");
        String origin = file.getOriginalFilename() == null ? "file" : file.getOriginalFilename();
        String ext = origin.contains(".") ? origin.substring(origin.lastIndexOf('.') + 1).toLowerCase() : "";
        if (!ALLOW.contains(ext)) throw new BizException("仅支持 jpg/png/webp/pdf 格式");
        if (file.getSize() > 20L * 1024 * 1024) throw new BizException("单个文件不得超过 20MB");
        String month = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMM"));
        Path dir = Paths.get(uploadDir, month).toAbsolutePath().normalize();
        Files.createDirectories(dir);
        String name = UUID.randomUUID().toString().replace("-", "") + "." + ext;
        File target = new File(dir.toFile(), name);
        file.transferTo(target);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("path", "/uploads/" + month + "/" + name);
        m.put("fileName", origin);
        m.put("size", file.getSize());
        m.put("uploader", UserContext.name());
        return R.ok(m);
    }}
}}
"""

for path, content in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
print("生成", len(FILES), "个核心控制器")
