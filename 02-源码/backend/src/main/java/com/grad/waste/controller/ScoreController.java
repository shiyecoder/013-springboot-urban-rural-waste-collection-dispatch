package com.grad.waste.controller;

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
public class ScoreController {

    private final DispatchScoreMapper mapper;

    public ScoreController(DispatchScoreMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<DispatchScore>> page(@RequestParam(defaultValue = "1") long page,
                                             @RequestParam(defaultValue = "10") long size,
                                             @RequestParam(required = false) String grade,
                                             @RequestParam(required = false) Long orderId) {
        LambdaQueryWrapper<DispatchScore> w = new LambdaQueryWrapper<>();
        if (grade != null && !grade.isBlank()) w.eq(DispatchScore::getGrade, grade);
        if (orderId != null) w.eq(DispatchScore::getOrderId, orderId);
        w.orderByDesc(DispatchScore::getId);
        Page<DispatchScore> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    /** 采纳率 / 人工调整率，用于验证创新模块有效性 */
    @GetMapping("/effect")
    public R<java.util.Map<String, Object>> effect() {
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
    }
}
