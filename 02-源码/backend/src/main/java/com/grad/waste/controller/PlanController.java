package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.CollectionPlan;
import com.grad.waste.mapper.CollectionPlanMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 周期计划管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/plan")
public class PlanController {

    private final CollectionPlanMapper mapper;

    public PlanController(CollectionPlanMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<CollectionPlan>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<CollectionPlan> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("plan_code", kw));
            }
            if (status != null && !status.isBlank()) w.eq("status", status);
        w.orderByDesc("id");
        Page<CollectionPlan> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<CollectionPlan>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<CollectionPlan>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<CollectionPlan> get(@PathVariable Long id) {
        CollectionPlan o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<CollectionPlan> add(@RequestBody CollectionPlan o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<CollectionPlan> update(@PathVariable Long id, @RequestBody CollectionPlan o) {
        if (mapper.selectById(id) == null) throw new BizException("记录不存在或已删除");
        mapper.updateById(o);
        return R.ok(o);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        mapper.deleteById(id);
        return R.ok();
    }
}
