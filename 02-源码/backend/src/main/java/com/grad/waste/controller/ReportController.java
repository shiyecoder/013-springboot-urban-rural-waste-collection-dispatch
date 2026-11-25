package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.grad.waste.common.R;
import com.grad.waste.entity.*;
import com.grad.waste.mapper.*;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 环卫运营看板：6 个核心指标 + 6 个图表。
 * 全部由后端聚合，前端不做二次全表统计，保证图表值与明细总数一致。
 */
@RestController
@RequestMapping("/api/report")
public class ReportController {

    private final DispatchOrderMapper orderMapper;
    private final CollectionPointMapper pointMapper;
    private final VehicleMapper vehicleMapper;
    private final WeighingRecordMapper weighMapper;
    private final ComplaintMapper complaintMapper;
    private final ExceptionRecordMapper exceptionMapper;
    private final DispatchScoreMapper scoreMapper;
    private final OverflowReportMapper overflowMapper;

    public ReportController(DispatchOrderMapper orderMapper, CollectionPointMapper pointMapper,
                            VehicleMapper vehicleMapper, WeighingRecordMapper weighMapper,
                            ComplaintMapper complaintMapper, ExceptionRecordMapper exceptionMapper,
                            DispatchScoreMapper scoreMapper, OverflowReportMapper overflowMapper) {
        this.orderMapper = orderMapper;
        this.pointMapper = pointMapper;
        this.vehicleMapper = vehicleMapper;
        this.weighMapper = weighMapper;
        this.complaintMapper = complaintMapper;
        this.exceptionMapper = exceptionMapper;
        this.scoreMapper = scoreMapper;
        this.overflowMapper = overflowMapper;
    }

    @GetMapping("/dashboard")
    public R<Map<String, Object>> dashboard() {
        LocalDateTime from = LocalDateTime.now().minusDays(30);
        List<DispatchOrder> orders = orderMapper.selectList(new LambdaQueryWrapper<DispatchOrder>()
                .ge(DispatchOrder::getCreateTime, from));
        Map<String, Object> m = new LinkedHashMap<>();

        // 核心指标
        List<WeighingRecord> weighs = weighMapper.selectList(new LambdaQueryWrapper<WeighingRecord>()
                .ge(WeighingRecord::getWeighTime, from));
        BigDecimal volume = weighs.stream().map(WeighingRecord::getNetWeight)
                .filter(Objects::nonNull).reduce(BigDecimal.ZERO, BigDecimal::add);
        long done = orders.stream().filter(o -> "DONE".equals(o.getStatus())).count();
        long total = orders.size();
        long overflow = pointMapper.selectCount(new LambdaQueryWrapper<CollectionPoint>()
                .eq(CollectionPoint::getStatus, "OVERFLOW"));
        long vehicles = vehicleMapper.selectCount(null);
        long busy = vehicleMapper.selectCount(new LambdaQueryWrapper<Vehicle>()
                .in(Vehicle::getStatus, "BUSY"));
        long complaints = complaintMapper.selectCount(new LambdaQueryWrapper<Complaint>()
                .ge(Complaint::getHappenTime, from));
        long abnormal = exceptionMapper.selectCount(new LambdaQueryWrapper<ExceptionRecord>()
                .ne(ExceptionRecord::getStatus, "CLOSED"));

        Map<String, Object> kpi = new LinkedHashMap<>();
        kpi.put("volume", volume);
        kpi.put("onTimeRate", total == 0 ? 0 : Math.round(done * 1000.0 / total) / 10.0);
        kpi.put("overflowPoints", overflow);
        kpi.put("vehicleUsage", vehicles == 0 ? 0 : Math.round(busy * 1000.0 / vehicles) / 10.0);
        kpi.put("complaints", complaints);
        kpi.put("abnormalOpen", abnormal);
        kpi.put("orderTotal", total);
        kpi.put("doneTotal", done);
        m.put("kpi", kpi);

        // 趋势：近 14 天清运量与任务数
        List<String> dates = new ArrayList<>();
        List<Double> vols = new ArrayList<>();
        List<Integer> cnts = new ArrayList<>();
        for (int i = 13; i >= 0; i--) {
            LocalDate d = LocalDate.now().minusDays(i);
            dates.add(String.format("%02d-%02d", d.getMonthValue(), d.getDayOfMonth()));
            LocalDateTime s = d.atStartOfDay();
            LocalDateTime e = s.plusDays(1);
            double v = weighMapper.selectList(new LambdaQueryWrapper<WeighingRecord>()
                            .ge(WeighingRecord::getWeighTime, s).lt(WeighingRecord::getWeighTime, e))
                    .stream().map(WeighingRecord::getNetWeight).filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add).doubleValue();
            vols.add(Math.round(v * 10) / 10.0);
            cnts.add(orderMapper.selectList(new LambdaQueryWrapper<DispatchOrder>()
                    .ge(DispatchOrder::getPlanTime, s).lt(DispatchOrder::getPlanTime, e)).size());
        }
        m.put("trend", Map.of("dates", dates, "volume", vols, "orders", cnts));

        // 状态分布
        Map<String, String> stName = new LinkedHashMap<>();
        stName.put("PENDING_DISPATCH", "待派车");
        stName.put("ACCEPTED", "已接单");
        stName.put("RUNNING", "清运中");
        stName.put("PENDING_CONFIRM", "待确认");
        stName.put("DONE", "已完成");
        stName.put("CANCELED", "已取消");
        stName.put("ABNORMAL", "异常");
        List<Map<String, Object>> statusDist = new ArrayList<>();
        stName.forEach((k, v) -> {
            long c = orders.stream().filter(o -> k.equals(o.getStatus())).count();
            statusDist.add(Map.of("name", v, "value", c));
        });
        m.put("statusDist", statusDist);

        // 垃圾类型构成（按点位容量汇总，口径稳定）
        List<CollectionPoint> points = pointMapper.selectList(null);
        Map<String, Double> wt = new LinkedHashMap<>();
        for (CollectionPoint p : points) {
            wt.merge(p.getWasteType(), p.getCapacity().doubleValue(), Double::sum);
        }
        List<Map<String, Object>> wasteType = new ArrayList<>();
        wt.forEach((k, v) -> wasteType.add(Map.of("name", k, "value", Math.round(v * 10) / 10.0)));
        m.put("wasteType", wasteType);

        // 区域任务排行
        Map<String, Integer> area = new LinkedHashMap<>();
        for (DispatchOrder o : orders) {
            String key = o.getPointSummary() == null ? "未分区" : o.getPointSummary().split("、")[0];
            area.merge(key, 1, Integer::sum);
        }
        List<Map<String, Object>> areaRank = new ArrayList<>();
        area.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).limit(5)
                .forEach(e -> areaRank.add(Map.of("name", e.getKey(), "value", e.getValue())));
        m.put("areaRank", areaRank);

        // 准时率对比（按状态分组粗算）
        List<Map<String, Object>> onTime = new ArrayList<>();
        for (String k : List.of("已完成", "待确认", "清运中", "待派车")) {
            String code = switch (k) {
                case "已完成" -> "DONE";
                case "待确认" -> "PENDING_CONFIRM";
                case "清运中" -> "RUNNING";
                default -> "PENDING_DISPATCH";
            };
            long c = orders.stream().filter(o -> code.equals(o.getStatus())).count();
            onTime.add(Map.of("name", k, "value", c));
        }
        m.put("onTimeByStatus", onTime);

        // 调度推荐结果分布
        List<DispatchScore> scores = scoreMapper.selectList(null);
        Map<String, String> gradeName = Map.of("P1", "强烈推荐", "P2", "建议派车", "P3", "可延后", "NONE", "不推荐");
        List<Map<String, Object>> scoreDist = new ArrayList<>();
        gradeName.forEach((k, v) -> {
            long c = scores.stream().filter(s -> k.equals(s.getGrade())).count();
            scoreDist.add(Map.of("name", v, "value", c));
        });
        long adopted = scores.stream().filter(s -> s.getAdopted() != null && s.getAdopted() == 1).count();
        long manual = scores.stream().filter(s -> s.getManualAdjust() != null && s.getManualAdjust() == 1).count();
        m.put("scoreDist", scoreDist);
        m.put("adoptRate", scores.isEmpty() ? 0 : Math.round(adopted * 1000.0 / scores.size()) / 10.0);
        m.put("manualRate", scores.isEmpty() ? 0 : Math.round(manual * 1000.0 / scores.size()) / 10.0);
        m.put("overflowPending", overflowMapper.selectCount(new LambdaQueryWrapper<OverflowReport>()
                .eq(OverflowReport::getStatus, "PENDING")));
        return R.ok(m);
    }
}
