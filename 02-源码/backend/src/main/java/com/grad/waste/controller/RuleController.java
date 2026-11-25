package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.DispatchRule;
import com.grad.waste.mapper.DispatchRuleMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 调度规则管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/rule")
public class RuleController {

    private final DispatchRuleMapper mapper;

    public RuleController(DispatchRuleMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<DispatchRule>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<DispatchRule> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("rule_name", kw));
            }

        w.orderByDesc("id");
        Page<DispatchRule> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<DispatchRule>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<DispatchRule>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<DispatchRule> get(@PathVariable Long id) {
        DispatchRule o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<DispatchRule> add(@RequestBody DispatchRule o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<DispatchRule> update(@PathVariable Long id, @RequestBody DispatchRule o) {
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
