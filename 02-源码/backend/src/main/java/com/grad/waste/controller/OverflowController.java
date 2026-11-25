package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.OverflowReport;
import com.grad.waste.mapper.OverflowReportMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 临时报满管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/overflow")
public class OverflowController {

    private final OverflowReportMapper mapper;

    public OverflowController(OverflowReportMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<OverflowReport>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<OverflowReport> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("report_no", kw));
            }
            if (status != null && !status.isBlank()) w.eq("status", status);
        w.orderByDesc("id");
        Page<OverflowReport> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<OverflowReport>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<OverflowReport>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<OverflowReport> get(@PathVariable Long id) {
        OverflowReport o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<OverflowReport> add(@RequestBody OverflowReport o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<OverflowReport> update(@PathVariable Long id, @RequestBody OverflowReport o) {
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
