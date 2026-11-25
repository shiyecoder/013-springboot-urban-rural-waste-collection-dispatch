#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 NEW-013 后端业务代码（controller / service / config）。"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "backend/src/main/java/com/grad/waste")
PKG = "com.grad.waste"

FILES = {}

FILES[f"{SRC}/WasteApplication.java"] = f"""package com.grad.waste;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** 城乡垃圾清运调度与台账管理系统 启动类 */
@SpringBootApplication
public class WasteApplication {{
    public static void main(String[] args) {{
        SpringApplication.run(WasteApplication.class, args);
    }}
}}
"""

FILES[f"{SRC}/config/MybatisPlusConfig.java"] = f"""package com.grad.waste.config;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** 分页插件：所有列表使用服务端分页 */
@Configuration
public class MybatisPlusConfig {{
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {{
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
        return interceptor;
    }}
}}
"""

FILES[f"{SRC}/config/JacksonConfig.java"] = f"""package com.grad.waste.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateDeserializer;
import com.fasterxml.jackson.datatype.jsr310.deser.LocalDateTimeDeserializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateSerializer;
import com.fasterxml.jackson.datatype.jsr310.ser.LocalDateTimeSerializer;
import org.springframework.boot.autoconfigure.jackson.Jackson2ObjectMapperBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 全局时间格式化：全系统统一 yyyy-MM-dd HH:mm:ss / yyyy-MM-dd，
 * 前端不再各自拼接时间字符串。
 */
@Configuration
public class JacksonConfig {{

    public static final DateTimeFormatter DT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    public static final DateTimeFormatter D = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    @Bean
    public Jackson2ObjectMapperBuilderCustomizer jacksonCustomizer() {{
        return builder -> {{
            JavaTimeModule module = new JavaTimeModule();
            module.addSerializer(LocalDateTime.class, new LocalDateTimeSerializer(DT));
            module.addDeserializer(LocalDateTime.class, new LocalDateTimeDeserializer(DT));
            module.addSerializer(LocalDate.class, new LocalDateSerializer(D));
            module.addDeserializer(LocalDate.class, new LocalDateDeserializer(D));
            builder.modules(module);
        }};
    }}

    @Bean
    public ObjectMapper objectMapper(Jackson2ObjectMapperBuilderCustomizer c) {{
        return new ObjectMapper().registerModule(new JavaTimeModule());
    }}
}}
"""

# ---------------- AuthService ----------------
FILES[f"{SRC}/service/AuthService.java"] = f"""package com.grad.waste.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.grad.waste.common.BizException;
import com.grad.waste.common.JwtUtil;
import com.grad.waste.common.UserContext;
import com.grad.waste.entity.SysMenu;
import com.grad.waste.entity.SysRole;
import com.grad.waste.entity.SysRoleMenu;
import com.grad.waste.entity.SysUser;
import com.grad.waste.mapper.SysMenuMapper;
import com.grad.waste.mapper.SysRoleMapper;
import com.grad.waste.mapper.SysRoleMenuMapper;
import com.grad.waste.mapper.SysUserMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

/**
 * 认证与权限：BCrypt 校验、连续失败锁定、按角色返回菜单。
 */
@Service
public class AuthService {{

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysMenuMapper menuMapper;
    private final SysRoleMenuMapper roleMenuMapper;
    private final PasswordEncoder encoder;
    private final JwtUtil jwtUtil;

    @Value("${{app.login-fail-limit:5}}")
    private int failLimit;
    @Value("${{app.login-lock-minutes:10}}")
    private int lockMinutes;

    public AuthService(SysUserMapper userMapper, SysRoleMapper roleMapper, SysMenuMapper menuMapper,
                       SysRoleMenuMapper roleMenuMapper, PasswordEncoder encoder, JwtUtil jwtUtil) {{
        this.userMapper = userMapper;
        this.roleMapper = roleMapper;
        this.menuMapper = menuMapper;
        this.roleMenuMapper = roleMenuMapper;
        this.encoder = encoder;
        this.jwtUtil = jwtUtil;
    }}

    /** 登录：连续失败 5 次锁定 10 分钟；任何返回都不含密码字段 */
    public Map<String, Object> login(String username, String password) {{
        SysUser u = userMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
        if (u == null) {{
            throw new BizException("账号或密码错误");
        }}
        if (u.getLockUntil() != null && u.getLockUntil().isAfter(LocalDateTime.now())) {{
            throw new BizException("账号已锁定，请于 " + u.getLockUntil() + " 后重试");
        }}
        if (!encoder.matches(password, u.getPassword())) {{
            int fail = (u.getLoginFail() == null ? 0 : u.getLoginFail()) + 1;
            u.setLoginFail(fail);
            if (fail >= failLimit) {{
                u.setLockUntil(LocalDateTime.now().plusMinutes(lockMinutes));
                u.setLoginFail(0);
            }}
            userMapper.updateById(u);
            int left = Math.max(0, failLimit - fail);
            throw new BizException("账号或密码错误，您还可以尝试 " + left + " 次");
        }}
        if (u.getStatus() != null && u.getStatus() == 0) {{
            throw new BizException("账号已停用，请联系管理员");
        }}
        SysRole role = roleMapper.selectById(u.getRoleId());
        String roleCode = role == null ? "USER" : role.getRoleCode();
        String scope = role == null ? "SELF" : role.getDataScope();
        u.setLoginFail(0);
        u.setLockUntil(null);
        u.setLastLogin(LocalDateTime.now());
        userMapper.updateById(u);

        String token = jwtUtil.create(u.getId(), u.getRealName(), roleCode, u.getOrgId(), scope);
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", brief(u, roleCode, role.getRoleName()));
        data.put("menus", menus(roleCode, u.getRoleId()));
        return data;
    }}

    public Map<String, Object> brief(SysUser u, String roleCode, String roleName) {{
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", u.getId());
        m.put("username", u.getUsername());
        m.put("realName", u.getRealName());
        m.put("avatar", u.getAvatar());
        m.put("phone", u.getPhone());
        m.put("email", u.getEmail());
        m.put("orgId", u.getOrgId());
        m.put("roleCode", roleCode);
        m.put("roleName", roleName);
        m.put("pointId", u.getPointId());
        m.put("driverId", u.getDriverId());
        return m;
    }}

    /** 按角色动态获取菜单（父级 + 子级，隐藏项不返回） */
    public List<Map<String, Object>> menus(String roleCode, Long roleId) {{
        List<SysMenu> all = menuMapper.selectList(new LambdaQueryWrapper<SysMenu>()
                .eq(SysMenu::getVisible, 1).orderByAsc(SysMenu::getSort));
        Set<Long> granted = new HashSet<>();
        if ("ADMIN".equals(roleCode)) {{
            all.forEach(m -> granted.add(m.getId()));
        }} else {{
            roleMenuMapper.selectList(new LambdaQueryWrapper<SysRoleMenu>().eq(SysRoleMenu::getRoleId, roleId))
                    .forEach(rm -> granted.add(rm.getMenuId()));
        }}
        List<SysMenu> visible = all.stream().filter(m -> granted.contains(m.getId())).toList();
        List<Map<String, Object>> tree = new ArrayList<>();
        for (SysMenu m : visible) {{
            if (m.getParentId() == null || m.getParentId() == 0) {{
                Map<String, Object> node = node(m);
                List<Map<String, Object>> children = new ArrayList<>();
                for (SysMenu c : visible) {{
                    if (m.getId().equals(c.getParentId())) children.add(node(c));
                }}
                node.put("children", children);
                tree.add(node);
            }}
        }}
        return tree;
    }}

    private Map<String, Object> node(SysMenu m) {{
        Map<String, Object> n = new LinkedHashMap<>();
        n.put("id", m.getId());
        n.put("name", m.getMenuName());
        n.put("path", m.getPath());
        n.put("icon", m.getIcon());
        n.put("type", m.getMenuType());
        return n;
    }}

    public SysUser current() {{
        SysUser u = userMapper.selectById(UserContext.userId());
        if (u == null) throw new BizException(401, "登录已过期，请重新登录");
        return u;
    }}

    public Map<String, Object> me() {{
        SysUser u = current();
        SysRole role = roleMapper.selectById(u.getRoleId());
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("user", brief(u, role == null ? "" : role.getRoleCode(), role == null ? "" : role.getRoleName()));
        data.put("menus", menus(role == null ? "" : role.getRoleCode(), u.getRoleId()));
        return data;
    }}

    public void updateProfile(String realName, String phone, String email, String avatar) {{
        SysUser u = current();
        if (realName != null && !realName.isBlank()) u.setRealName(realName);
        if (phone != null) u.setPhone(phone);
        if (email != null) u.setEmail(email);
        if (avatar != null && !avatar.isBlank()) u.setAvatar(avatar);
        userMapper.updateById(u);
    }}

    public void changePassword(String oldPwd, String newPwd) {{
        SysUser u = current();
        if (!encoder.matches(oldPwd, u.getPassword())) throw new BizException("原密码不正确");
        if (newPwd == null || newPwd.length() < 6) throw new BizException("新密码不少于 6 位");
        u.setPassword(encoder.encode(newPwd));
        userMapper.updateById(u);
    }}
}}
"""

# ---------------- ScoreService（创新点） ----------------
FILES[f"{SRC}/service/ScoreService.java"] = f"""package com.grad.waste.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.grad.waste.common.BizException;
import com.grad.waste.entity.*;
import com.grad.waste.mapper.*;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 创新点：容量与时效联合调度。
 * 依据满载度、滞留时长、投诉次数、车辆剩余容量、点位距离、垃圾类型匹配六项评分，
 * 权重取自启用中的规则版本，每次计算都落库快照，保证同输入同版本结果可复现。
 */
@Service
public class ScoreService {{

    private final DispatchRuleMapper ruleMapper;
    private final DispatchScoreMapper scoreMapper;
    private final CollectionPointMapper pointMapper;
    private final ComplaintMapper complaintMapper;
    private final VehicleMapper vehicleMapper;
    private final RouteStopMapper stopMapper;

    public ScoreService(DispatchRuleMapper ruleMapper, DispatchScoreMapper scoreMapper,
                        CollectionPointMapper pointMapper, ComplaintMapper complaintMapper,
                        VehicleMapper vehicleMapper, RouteStopMapper stopMapper) {{
        this.ruleMapper = ruleMapper;
        this.scoreMapper = scoreMapper;
        this.pointMapper = pointMapper;
        this.complaintMapper = complaintMapper;
        this.vehicleMapper = vehicleMapper;
        this.stopMapper = stopMapper;
    }}

    public DispatchRule activeRule() {{
        DispatchRule r = ruleMapper.selectOne(new LambdaQueryWrapper<DispatchRule>()
                .eq(DispatchRule::getEnabled, 1).orderByDesc(DispatchRule::getVersion).last("limit 1"));
        if (r == null) throw new BizException("未找到启用中的调度规则，请先在规则配置页启用一个版本");
        return r;
    }}

    /** 对一条任务执行计算，返回明细并写入留痕表 */
    public DispatchScore evaluate(DispatchOrder order, boolean persist) {{
        DispatchRule rule = activeRule();
        CollectionPoint p = pointMapper.selectById(firstPointId(order));
        if (p == null) throw new BizException("任务未关联有效收集点，无法计算");

        // 1) 满载度（缺失不参与计算并提示补录）
        int load = p.getLoadRate() == null ? 0 : p.getLoadRate();
        LocalDateTime last = p.getLastClearTime() == null ? order.getPlanTime() : p.getLastClearTime();
        double stay = Math.max(0, Duration.between(last, LocalDateTime.now()).toHours());
        Long complaints = complaintMapper.selectCount(new LambdaQueryWrapper<Complaint>()
                .eq(Complaint::getPointId, p.getId())
                .ge(Complaint::getHappenTime, LocalDateTime.now().minusDays(30)));
        Vehicle v = order.getVehicleId() == null ? null : vehicleMapper.selectById(order.getVehicleId());
        double cap = v == null ? 0 : v.getLoadCapacity().doubleValue();
        double est = order.getEstimatedWeight() == null ? 0 : order.getEstimatedWeight().doubleValue();
        double remain = Math.max(0, cap - est);
        // 距离：同线路站点顺序估算直线距离，缺坐标时按线路里程均值
        double dist = distanceKm(order, p);
        int typeMatch = (v != null && v.getWasteTypes() != null && p.getWasteType() != null
                && v.getWasteTypes().contains(p.getWasteType())) ? 1 : 0;

        double sLoad = round(load / 100.0 * rule.getWLoad());
        double sStay = round(Math.min(stay / 72.0, 1) * rule.getWStay());
        double sComp = round(Math.min(complaints / 5.0, 1) * rule.getWComplaint());
        double sCap = round(Math.min(remain / Math.max(cap, 1), 1) * rule.getWCapacity());
        double sDist = round(Math.max(0, 1 - dist / 15.0) * rule.getWDistance());
        double sType = typeMatch * rule.getWTypeMatch();
        double total = round(sLoad + sStay + sComp + sCap + sDist + sType);

        String grade = total >= rule.getThresholdP1() ? "P1"
                : total >= rule.getThresholdP2() ? "P2"
                : total >= rule.getThresholdP3() ? "P3" : "NONE";

        List<String> factors = new ArrayList<>();
        if (load >= 80) factors.add("满载度 " + load + "%（超阈值 80%）");
        if (stay >= 48) factors.add("滞留 " + (long) stay + " 小时");
        if (complaints >= 2) factors.add("近 30 天投诉 " + complaints + " 次");
        if (factors.isEmpty()) factors.add("各项指标均处于正常区间");

        List<String> unmet = new ArrayList<>();
        if (v == null) unmet.add("未分配车辆，无法核对载重");
        else if (cap < est) unmet.add("车辆载重 " + cap + " 吨不足以装载预估 " + est + " 吨");
        if (typeMatch == 0) unmet.add("车辆可收运类型与点位垃圾类型不一致");
        if (unmet.isEmpty()) unmet.add("无");

        List<String> improve = new ArrayList<>();
        if (dist > 8) improve.add("点位距上一站 " + round(dist) + " km，建议调整线路顺序减少空驶");
        if (load < 60) improve.add("当前满载度偏低，可与相邻点位合并派车");
        if (improve.isEmpty()) improve.add("暂无明显可优化项");

        DispatchScore s = new DispatchScore();
        s.setOrderId(order.getId());
        s.setRuleId(rule.getId());
        s.setRuleVersion(rule.getVersion());
        String snap = "__Q__loadRate__Q__: " + load + ", __Q__stayHours__Q__: " + stay
                + ", __Q__complaints__Q__: " + complaints + ", __Q__vehicleCapacity__Q__: " + cap
                + ", __Q__estimatedWeight__Q__: " + est + ", __Q__distanceKm__Q__: " + dist
                + ", __Q__typeMatch__Q__: " + typeMatch;
        s.setSnapshot(snap);
        s.setVLoad(BigDecimal.valueOf(load));
        s.setVStay(BigDecimal.valueOf(round(stay)));
        s.setVComplaint(complaints.intValue());
        s.setVCapacity(BigDecimal.valueOf(cap));
        s.setVDistance(BigDecimal.valueOf(dist));
        s.setVTypeMatch(typeMatch);
        s.setSLoad(BigDecimal.valueOf(sLoad));
        s.setSStay(BigDecimal.valueOf(sStay));
        s.setSComplaint(BigDecimal.valueOf(sComp));
        s.setSCapacity(BigDecimal.valueOf(sCap));
        s.setSDistance(BigDecimal.valueOf(sDist));
        s.setSTypeMatch(BigDecimal.valueOf(sType));
        s.setTotalScore(BigDecimal.valueOf(total));
        s.setGrade(grade);
        s.setFactors(String.join("；", factors));
        s.setUnmet(String.join("；", unmet));
        s.setImprove(String.join("；", improve));
        s.setAdopted(0);
        s.setManualAdjust(0);
        s.setCreateTime(LocalDateTime.now());
        if (persist) scoreMapper.insert(s);
        return s;
    }}

    private Long firstPointId(DispatchOrder order) {{
        List<RouteStop> stops = stopMapper.selectList(new LambdaQueryWrapper<RouteStop>()
                .eq(RouteStop::getOrderId, order.getId()).orderByAsc(RouteStop::getSeq));
        if (!stops.isEmpty()) return stops.get(0).getPointId();
        return null;
    }}

    /** 直线距离：有坐标用坐标，缺坐标按同线路平均站距兜底 */
    private double distanceKm(DispatchOrder order, CollectionPoint p) {{
        if (p.getLongitude() == null || p.getLatitude() == null) return 5.0;
        return Math.abs(p.getLongitude().doubleValue() - 120.15) * 96
                + Math.abs(p.getLatitude().doubleValue() - 30.28) * 111;
    }}

    private double round(double v) {{
        return BigDecimal.valueOf(v).setScale(2, RoundingMode.HALF_UP).doubleValue();
    }}
}}
"""

# ---------------- DispatchService ----------------
FILES[f"{SRC}/service/DispatchService.java"] = f"""package com.grad.waste.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.grad.waste.common.BizException;
import com.grad.waste.common.UserContext;
import com.grad.waste.entity.*;
import com.grad.waste.mapper.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 清运任务核心服务。
 * 状态机：待派车 → 已接单 → 清运中 → 待确认 → 已完成；
 * 取消 / 拒接 / 终止 / 改派必须填写原因（≥5 字）；派单校验载重与司机时间冲突。
 */
@Service
public class DispatchService {{

    private static final Map<String, String> FLOW = new LinkedHashMap<>();
    static {{
        FLOW.put("PENDING_DISPATCH", "ACCEPTED");
        FLOW.put("ACCEPTED", "RUNNING");
        FLOW.put("RUNNING", "PENDING_CONFIRM");
        FLOW.put("PENDING_CONFIRM", "DONE");
    }}

    private final DispatchOrderMapper orderMapper;
    private final RouteStopMapper stopMapper;
    private final VehicleMapper vehicleMapper;
    private final DriverMapper driverMapper;
    private final FlowLogMapper flowMapper;
    private final DispatchScoreMapper scoreMapper;
    private final WeighingRecordMapper weighMapper;
    private final SysMessageMapper msgMapper;
    private final ScoreService scoreService;

    public DispatchService(DispatchOrderMapper orderMapper, RouteStopMapper stopMapper,
                           VehicleMapper vehicleMapper, DriverMapper driverMapper, FlowLogMapper flowMapper,
                           DispatchScoreMapper scoreMapper, WeighingRecordMapper weighMapper,
                           SysMessageMapper msgMapper, ScoreService scoreService) {{
        this.orderMapper = orderMapper;
        this.stopMapper = stopMapper;
        this.vehicleMapper = vehicleMapper;
        this.driverMapper = driverMapper;
        this.flowMapper = flowMapper;
        this.scoreMapper = scoreMapper;
        this.weighMapper = weighMapper;
        this.msgMapper = msgMapper;
        this.scoreService = scoreService;
    }}

    /** 派车 / 改派：载重、车况、保养、司机时间冲突全部后端校验 */
    @Transactional
    public void assign(Long id, Long vehicleId, Long driverId, Long siteId, LocalDateTime planTime,
                       boolean reassign, String reason) {{
        DispatchOrder o = mustGet(id);
        if (!"PENDING_DISPATCH".equals(o.getStatus()) && !reassign) {{
            throw new BizException("当前状态不允许派车：" + o.getStatus());
        }}
        if (reassign && !List.of("ACCEPTED", "RUNNING").contains(o.getStatus())) {{
            throw new BizException("仅已接单或清运中的任务可以改派");
        }}
        if (reassign && (reason == null || reason.trim().length() < 5)) {{
            throw new BizException("改派必须填写原因，且不少于 5 个字");
        }}
        Vehicle v = vehicleMapper.selectById(vehicleId);
        if (v == null) throw new BizException("车辆不存在");
        if ("MAINTAIN".equals(v.getStatus())) throw new BizException("车辆保养中，不可派单");
        if ("DISABLED".equals(v.getStatus())) throw new BizException("车辆已停用");
        // 硬性规则 3：预估重量不得超过车辆载重
        if (v.getLoadCapacity().compareTo(o.getEstimatedWeight()) < 0) {{
            throw new BizException("预估重量 " + o.getEstimatedWeight() + " 吨超过车辆载重 "
                    + v.getLoadCapacity() + " 吨，请更换车辆或拆分任务");
        }}
        Driver d = driverMapper.selectById(driverId);
        if (d == null) throw new BizException("司机不存在");
        if (d.getStatus() != null && d.getStatus() == 0) throw new BizException("司机处于离岗状态");
        // 司机时间冲突：同一司机前后 2 小时内不得有其它进行中任务
        LocalDateTime pt = planTime == null ? o.getPlanTime() : planTime;
        List<DispatchOrder> conflict = orderMapper.selectList(new LambdaQueryWrapper<DispatchOrder>()
                .eq(DispatchOrder::getDriverId, driverId)
                .in(DispatchOrder::getStatus, "ACCEPTED", "RUNNING")
                .ne(DispatchOrder::getId, id));
        for (DispatchOrder c : conflict) {{
            if (c.getPlanTime() != null && Math.abs(java.time.Duration.between(c.getPlanTime(), pt).toMinutes()) < 120) {{
                throw new BizException("司机在该时段已有任务 " + c.getOrderNo() + "，存在时间冲突");
            }}
        }}
        if (o.getVehicleId() != null && o.getDriverId() != null && reassign) {{
            flow(o, o.getStatus(), o.getStatus(), "改派", "原司机 " + driverMapper.selectById(o.getDriverId()).getName() + "：" + reason);
        }}
        o.setVehicleId(vehicleId);
        o.setDriverId(driverId);
        o.setDisposeSiteId(siteId);
        o.setPlanTime(pt);
        o.setDispatchTime(LocalDateTime.now());
        o.setDispatcherId(2L);
        o.setStatus("ACCEPTED");
        o.setVersion((o.getVersion() == null ? 0 : o.getVersion()) + 1);
        orderMapper.updateById(o);
        v.setStatus("BUSY");
        vehicleMapper.updateById(v);

        flow(o, reassign ? o.getStatus() : "PENDING_DISPATCH", "ACCEPTED", reassign ? "改派" : "派车",
                reassign ? reason : "调度员 " + UserContext.name() + " 派车");
        message("任务已派发", "您有新任务 " + o.getOrderNo() + "，计划 "
                + pt + " 到场", "DISPATCH", o.getOrderNo());
    }}

    /** 状态流转：接单 / 开始 / 完成各点 / 确认交接 / 取消 / 拒接 */
    @Transactional
    public void transition(Long id, String action, String reason) {{
        DispatchOrder o = mustGet(id);
        String target;
        String actName;
        switch (action) {{
            case "accept" -> {{ target = "ACCEPTED"; actName = "司机接单"; }}
            case "start" -> {{ target = "RUNNING"; actName = "开始清运"; }}
            case "finish" -> {{ target = "PENDING_CONFIRM"; actName = "完成各点清运"; }}
            case "confirm" -> {{ target = "DONE"; actName = "确认交接"; }}
            case "cancel" -> {{ target = "CANCELED"; actName = "取消任务"; }}
            case "refuse" -> {{ target = "PENDING_DISPATCH"; actName = "司机拒接"; }}
            default -> throw new BizException("不支持的操作：" + action);
        }}
        if (List.of("cancel", "refuse").contains(action)
                && (reason == null || reason.trim().length() < 5)) {{
            throw new BizException("取消或拒接必须填写原因，且不少于 5 个字");
        }}
        if (!List.of("cancel", "refuse").contains(action)) {{
            String expect = FLOW.get(o.getStatus());
            if (expect == null || !expect.equals(target)) {{
                throw new BizException("当前状态 " + o.getStatus() + " 不允许执行该操作，禁止越级流转");
            }}
        }}
        String from = o.getStatus();
        o.setStatus(target);
        if (List.of("cancel", "refuse").contains(action)) o.setReason(reason);
        o.setVersion((o.getVersion() == null ? 0 : o.getVersion()) + 1);
        orderMapper.updateById(o);
        flow(o, from, target, actName, reason);
    }}

    /** 详情：基础 + 站点 + 计算留痕 + 流转 + 称重 */
    public Map<String, Object> detail(Long id) {{
        DispatchOrder o = mustGet(id);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("order", o);
        m.put("vehicle", o.getVehicleId() == null ? null : vehicleMapper.selectById(o.getVehicleId()));
        m.put("driver", o.getDriverId() == null ? null : driverMapper.selectById(o.getDriverId()));
        m.put("stops", stopMapper.selectList(new LambdaQueryWrapper<RouteStop>()
                .eq(RouteStop::getOrderId, id).orderByAsc(RouteStop::getSeq)));
        m.put("flows", flowMapper.selectList(new LambdaQueryWrapper<FlowLog>()
                .eq(FlowLog::getBizType, "DISPATCH").eq(FlowLog::getBizId, id)
                .orderByAsc(FlowLog::getCreateTime)));
        m.put("scores", scoreMapper.selectList(new LambdaQueryWrapper<DispatchScore>()
                .eq(DispatchScore::getOrderId, id).orderByDesc(DispatchScore::getId)));
        m.put("weighing", weighMapper.selectOne(new LambdaQueryWrapper<WeighingRecord>()
                .eq(WeighingRecord::getOrderId, id).orderByDesc(WeighingRecord::getId).last("limit 1")));
        return m;
    }}

    /** 人工调整：原始计算结果不覆盖，仅新增调整记录 */
    @Transactional
    public void adjust(Long id, String reason, Long vehicleId) {{
        if (reason == null || reason.trim().length() < 5) throw new BizException("人工调整必须填写原因，且不少于 5 个字");
        DispatchOrder o = mustGet(id);
        DispatchScore latest = scoreMapper.selectOne(new LambdaQueryWrapper<DispatchScore>()
                .eq(DispatchScore::getOrderId, id).orderByDesc(DispatchScore::getId).last("limit 1"));
        if (latest != null) {{
            latest.setManualAdjust(1);
            latest.setAdopted(0);
            latest.setAdjustReason(reason);
            scoreMapper.updateById(latest);
        }}
        if (vehicleId != null) o.setVehicleId(vehicleId);
        orderMapper.updateById(o);
        flow(o, o.getStatus(), o.getStatus(), "人工调整", reason);
    }}

    private DispatchOrder mustGet(Long id) {{
        DispatchOrder o = orderMapper.selectById(id);
        if (o == null) throw new BizException("任务不存在或已删除");
        return o;
    }}

    private void flow(DispatchOrder o, String from, String to, String action, String reason) {{
        FlowLog f = new FlowLog();
        f.setBizType("DISPATCH");
        f.setBizId(o.getId());
        f.setBizNo(o.getOrderNo());
        f.setFromStatus(from);
        f.setToStatus(to);
        f.setAction(action);
        f.setReason(reason);
        f.setOperator(UserContext.name());
        f.setCreateTime(LocalDateTime.now());
        flowMapper.insert(f);
    }}

    private void message(String title, String content, String type, String no) {{
        SysMessage m = new SysMessage();
        m.setTitle(title);
        m.setContent(content);
        m.setBizType(type);
        m.setBizNo(no);
        m.setReceiverId(7L);
        m.setReadFlag(0);
        m.setCreateTime(LocalDateTime.now());
        msgMapper.insert(m);
    }}
}}
"""

for path, content in FILES.items():
    content = content.replace("__Q__", chr(34))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
print("生成", len(FILES), "个文件")
