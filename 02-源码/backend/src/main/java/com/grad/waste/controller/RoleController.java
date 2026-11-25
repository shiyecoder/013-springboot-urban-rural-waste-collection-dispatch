package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.SysRole;
import com.grad.waste.entity.SysRoleMenu;
import com.grad.waste.mapper.SysRoleMapper;
import com.grad.waste.mapper.SysRoleMenuMapper;
import lombok.Data;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

/**
 * 角色管理：服务端分页、条件查询、增删改，以及「为角色分配菜单」授权。
 */
@RestController
@RequestMapping("/api/role")
public class RoleController {

    private final SysRoleMapper mapper;
    private final SysRoleMenuMapper roleMenuMapper;

    public RoleController(SysRoleMapper mapper, SysRoleMenuMapper roleMenuMapper) {
        this.mapper = mapper;
        this.roleMenuMapper = roleMenuMapper;
    }

    /** 分配菜单请求体：勾选的菜单 id 集合 */
    @Data
    public static class MenuAssign {
        private List<Long> menuIds;
    }

    /** 查询该角色已授权的菜单 id，前端据此回显勾选状态 */
    @GetMapping("/{id}/menus")
    public R<List<Long>> menuIds(@PathVariable Long id) {
        List<SysRoleMenu> list = roleMenuMapper.selectList(
                new QueryWrapper<SysRoleMenu>().eq("role_id", id));
        List<Long> ids = new ArrayList<>();
        for (SysRoleMenu rm : list) {
            ids.add(rm.getMenuId());
        }
        return R.ok(ids);
    }

    /** 保存角色菜单授权：先清空旧关系再按前端勾选结果重建，保证两侧一致 */
    @PutMapping("/{id}/menus")
    @Transactional
    public R<Void> saveMenus(@PathVariable Long id, @RequestBody MenuAssign body) {
        if (mapper.selectById(id) == null) {
            throw new BizException("记录不存在或已删除");
        }
        roleMenuMapper.delete(new QueryWrapper<SysRoleMenu>().eq("role_id", id));
        if (body != null && body.getMenuIds() != null) {
            for (Long menuId : body.getMenuIds()) {
                SysRoleMenu rm = new SysRoleMenu();
                rm.setRoleId(id);
                rm.setMenuId(menuId);
                roleMenuMapper.insert(rm);
            }
        }
        return R.ok();
    }

    @GetMapping("/page")
    public R<PageResult<SysRole>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<SysRole> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("role_name", kw).or().like("role_code", kw));
            }

        w.orderByDesc("id");
        Page<SysRole> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<SysRole>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<SysRole>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<SysRole> get(@PathVariable Long id) {
        SysRole o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<SysRole> add(@RequestBody SysRole o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<SysRole> update(@PathVariable Long id, @RequestBody SysRole o) {
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
