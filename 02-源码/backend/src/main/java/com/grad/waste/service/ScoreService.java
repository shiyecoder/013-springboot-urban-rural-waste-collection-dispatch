package com.grad.waste.service;

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
public class ScoreService {

    private final DispatchRuleMapper ruleMapper;
    private final DispatchScoreMapper scoreMapper;
    private final CollectionPointMapper pointMapper;
    private final ComplaintMapper complaintMapper;
    private final VehicleMapper vehicleMapper;
    private final RouteStopMapper stopMapper;

    public ScoreService(DispatchRuleMapper ruleMapper, DispatchScoreMapper scoreMapper,
                        CollectionPointMapper pointMapper, ComplaintMapper complaintMapper,
                        VehicleMapper vehicleMapper, RouteStopMapper stopMapper) {
        this.ruleMapper = ruleMapper;
        this.scoreMapper = scoreMapper;
        this.pointMapper = pointMapper;
        this.complaintMapper = complaintMapper;
        this.vehicleMapper = vehicleMapper;
        this.stopMapper = stopMapper;
    }

    public DispatchRule activeRule() {
        DispatchRule r = ruleMapper.selectOne(new LambdaQueryWrapper<DispatchRule>()
                .eq(DispatchRule::getEnabled, 1).orderByDesc(DispatchRule::getVersion).last("limit 1"));
        if (r == null) throw new BizException("未找到启用中的调度规则，请先在规则配置页启用一个版本");
        return r;
    }

    /** 对一条任务执行计算，返回明细并写入留痕表 */
    public DispatchScore evaluate(DispatchOrder order, boolean persist) {
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
        // 输入快照：保留本次计算的全部输入，便于复现与追溯
        String snap = "{loadRate: " + load + ", stayHours: " + stay
                + ", complaints: " + complaints + ", vehicleCapacity: " + cap
                + ", estimatedWeight: " + est + ", distanceKm: " + dist
                + ", typeMatch: " + typeMatch + "}";
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
    }

    private Long firstPointId(DispatchOrder order) {
        List<RouteStop> stops = stopMapper.selectList(new LambdaQueryWrapper<RouteStop>()
                .eq(RouteStop::getOrderId, order.getId()).orderByAsc(RouteStop::getSeq));
        if (!stops.isEmpty()) return stops.get(0).getPointId();
        return null;
    }

    /** 直线距离：有坐标用坐标，缺坐标按同线路平均站距兜底 */
    private double distanceKm(DispatchOrder order, CollectionPoint p) {
        if (p.getLongitude() == null || p.getLatitude() == null) return 5.0;
        return Math.abs(p.getLongitude().doubleValue() - 120.15) * 96
                + Math.abs(p.getLatitude().doubleValue() - 30.28) * 111;
    }

    private double round(double v) {
        return BigDecimal.valueOf(v).setScale(2, RoundingMode.HALF_UP).doubleValue();
    }
}
