package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.Driver;
import com.grad.waste.mapper.DriverMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 司机档案管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/driver")
public class DriverController {

    private final DriverMapper mapper;

    public DriverController(DriverMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<Driver>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<Driver> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("name", kw).or().like("phone", kw).or().like("driver_no", kw));
            }
            if (status != null && !status.isBlank()) w.eq("status", status);
        w.orderByDesc("id");
        Page<Driver> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<Driver>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<Driver>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<Driver> get(@PathVariable Long id) {
        Driver o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<Driver> add(@RequestBody Driver o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<Driver> update(@PathVariable Long id, @RequestBody Driver o) {
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
