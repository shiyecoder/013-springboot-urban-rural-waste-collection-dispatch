package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.Complaint;
import com.grad.waste.mapper.ComplaintMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 投诉记录管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/complaint")
public class ComplaintController {

    private final ComplaintMapper mapper;

    public ComplaintController(ComplaintMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<Complaint>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<Complaint> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("content", kw));
            }
            if (status != null && !status.isBlank()) w.eq("handle_status", status);
        w.orderByDesc("id");
        Page<Complaint> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<Complaint>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<Complaint>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<Complaint> get(@PathVariable Long id) {
        Complaint o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<Complaint> add(@RequestBody Complaint o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<Complaint> update(@PathVariable Long id, @RequestBody Complaint o) {
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
