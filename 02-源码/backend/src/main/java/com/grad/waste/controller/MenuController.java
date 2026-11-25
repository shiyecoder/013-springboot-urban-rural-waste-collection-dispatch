package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.SysMenu;
import com.grad.waste.mapper.SysMenuMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 菜单管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/menu")
public class MenuController {

    private final SysMenuMapper mapper;

    public MenuController(SysMenuMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<SysMenu>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<SysMenu> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("menu_name", kw));
            }

        w.orderByDesc("sort");
        Page<SysMenu> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<SysMenu>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<SysMenu>().orderByAsc("sort")));
    }

    @GetMapping("/{id}")
    public R<SysMenu> get(@PathVariable Long id) {
        SysMenu o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<SysMenu> add(@RequestBody SysMenu o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<SysMenu> update(@PathVariable Long id, @RequestBody SysMenu o) {
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
