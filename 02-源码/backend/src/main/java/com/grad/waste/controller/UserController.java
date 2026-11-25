package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.SysUser;
import com.grad.waste.mapper.SysUserMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 用户管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/user")
public class UserController {

    private final SysUserMapper mapper;

    public UserController(SysUserMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<SysUser>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<SysUser> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("username", kw).or().like("real_name", kw));
            }
            if (status != null && !status.isBlank()) w.eq("status", status);
        w.orderByDesc("id");
        Page<SysUser> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<SysUser>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<SysUser>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<SysUser> get(@PathVariable Long id) {
        SysUser o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<SysUser> add(@RequestBody SysUser o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<SysUser> update(@PathVariable Long id, @RequestBody SysUser o) {
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
