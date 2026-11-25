package com.grad.waste.controller;

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
public class DispatchController {

    private final DispatchOrderMapper orderMapper;
    private final DispatchScoreMapper scoreMapper;
    private final DispatchService dispatchService;
    private final ScoreService scoreService;

    public DispatchController(DispatchOrderMapper orderMapper, DispatchScoreMapper scoreMapper,
                              DispatchService dispatchService, ScoreService scoreService) {
        this.orderMapper = orderMapper;
        this.scoreMapper = scoreMapper;
        this.dispatchService = dispatchService;
        this.scoreService = scoreService;
    }

    @GetMapping("/page")
    public R<PageResult<DispatchOrder>> page(@RequestParam(defaultValue = "1") long page,
                                             @RequestParam(defaultValue = "10") long size,
                                             @RequestParam(required = false) String kw,
                                             @RequestParam(required = false) String status,
                                             @RequestParam(required = false) String date) {
        LambdaQueryWrapper<DispatchOrder> w = new LambdaQueryWrapper<>();
        if (kw != null && !kw.isBlank()) {
            w.and(x -> x.like(DispatchOrder::getOrderNo, kw).or().like(DispatchOrder::getPointSummary, kw));
        }
        if (status != null && !status.isBlank()) w.eq(DispatchOrder::getStatus, status);
        if (date != null && !date.isBlank()) {
            LocalDateTime d0 = LocalDateTime.parse(date + " 00:00:00", DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
            w.ge(DispatchOrder::getPlanTime, d0).lt(DispatchOrder::getPlanTime, d0.plusDays(1));
        }
        // 待本人处理优先、更新时间倒序
        w.orderByAsc(DispatchOrder::getStatus).orderByDesc(DispatchOrder::getUpdateTime);
        Page<DispatchOrder> p = orderMapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/{id}")
    public R<Map<String, Object>> detail(@PathVariable Long id) {
        return R.ok(dispatchService.detail(id));
    }

    @PostMapping("/{id}/assign")
    public R<Void> assign(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Long vehicleId = body.get("vehicleId") == null ? null : Long.valueOf(String.valueOf(body.get("vehicleId")));
        Long driverId = body.get("driverId") == null ? null : Long.valueOf(String.valueOf(body.get("driverId")));
        Long siteId = body.get("disposeSiteId") == null ? null : Long.valueOf(String.valueOf(body.get("disposeSiteId")));
        LocalDateTime planTime = null;
        if (body.get("planTime") != null) {
            String s = String.valueOf(body.get("planTime")).replace("T", " ");
            if (s.length() == 16) s = s + ":00";
            planTime = LocalDateTime.parse(s, DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        }
        dispatchService.assign(id, vehicleId, driverId, siteId, planTime, false, null);
        return R.ok();
    }

    @PostMapping("/{id}/reassign")
    public R<Void> reassign(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Long vehicleId = Long.valueOf(String.valueOf(body.get("vehicleId")));
        Long driverId = Long.valueOf(String.valueOf(body.get("driverId")));
        Long siteId = body.get("disposeSiteId") == null ? null : Long.valueOf(String.valueOf(body.get("disposeSiteId")));
        dispatchService.assign(id, vehicleId, driverId, siteId, null, true, String.valueOf(body.get("reason")));
        return R.ok();
    }

    @PostMapping("/{id}/transition")
    public R<Void> transition(@PathVariable Long id, @RequestBody Map<String, String> body) {
        dispatchService.transition(id, body.get("action"), body.get("reason"));
        return R.ok();
    }

    /** 执行「容量与时效联合调度」并返回明细依据，同时写留痕 */
    @PostMapping("/{id}/evaluate")
    public R<DispatchScore> evaluate(@PathVariable Long id) {
        DispatchOrder o = orderMapper.selectById(id);
        return R.ok(scoreService.evaluate(o, true));
    }

    @PostMapping("/{id}/adjust")
    public R<Void> adjust(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Long vehicleId = body.get("vehicleId") == null ? null : Long.valueOf(String.valueOf(body.get("vehicleId")));
        dispatchService.adjust(id, String.valueOf(body.get("reason")), vehicleId);
        return R.ok();
    }

    @GetMapping("/{id}/scores")
    public R<List<DispatchScore>> scores(@PathVariable Long id) {
        return R.ok(scoreMapper.selectList(new LambdaQueryWrapper<DispatchScore>()
                .eq(DispatchScore::getOrderId, id).orderByDesc(DispatchScore::getId)));
    }
}
