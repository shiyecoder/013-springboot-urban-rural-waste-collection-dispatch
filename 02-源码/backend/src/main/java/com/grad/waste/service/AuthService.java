package com.grad.waste.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.grad.waste.common.BizException;
import com.grad.waste.common.JwtUtil;
import com.grad.waste.common.UserContext;
import com.grad.waste.entity.SysMenu;
import com.grad.waste.entity.SysRole;
import com.grad.waste.entity.SysRoleMenu;
import com.grad.waste.entity.SysUser;
import com.grad.waste.mapper.SysMenuMapper;
import com.grad.waste.mapper.SysRoleMapper;
import com.grad.waste.mapper.SysRoleMenuMapper;
import com.grad.waste.mapper.SysUserMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

/**
 * 认证与权限：BCrypt 校验、连续失败锁定、按角色返回菜单。
 */
@Service
public class AuthService {

    private final SysUserMapper userMapper;
    private final SysRoleMapper roleMapper;
    private final SysMenuMapper menuMapper;
    private final SysRoleMenuMapper roleMenuMapper;
    private final PasswordEncoder encoder;
    private final JwtUtil jwtUtil;

    @Value("${app.login-fail-limit:5}")
    private int failLimit;
    @Value("${app.login-lock-minutes:10}")
    private int lockMinutes;

    public AuthService(SysUserMapper userMapper, SysRoleMapper roleMapper, SysMenuMapper menuMapper,
                       SysRoleMenuMapper roleMenuMapper, PasswordEncoder encoder, JwtUtil jwtUtil) {
        this.userMapper = userMapper;
        this.roleMapper = roleMapper;
        this.menuMapper = menuMapper;
        this.roleMenuMapper = roleMenuMapper;
        this.encoder = encoder;
        this.jwtUtil = jwtUtil;
    }

    /** 登录：连续失败 5 次锁定 10 分钟；任何返回都不含密码字段 */
    public Map<String, Object> login(String username, String password) {
        SysUser u = userMapper.selectOne(new LambdaQueryWrapper<SysUser>().eq(SysUser::getUsername, username));
        if (u == null) {
            throw new BizException("账号或密码错误");
        }
        if (u.getLockUntil() != null && u.getLockUntil().isAfter(LocalDateTime.now())) {
            throw new BizException("账号已锁定，请于 " + u.getLockUntil() + " 后重试");
        }
        if (!encoder.matches(password, u.getPassword())) {
            int fail = (u.getLoginFail() == null ? 0 : u.getLoginFail()) + 1;
            u.setLoginFail(fail);
            if (fail >= failLimit) {
                u.setLockUntil(LocalDateTime.now().plusMinutes(lockMinutes));
                u.setLoginFail(0);
            }
            userMapper.updateById(u);
            int left = Math.max(0, failLimit - fail);
            throw new BizException("账号或密码错误，您还可以尝试 " + left + " 次");
        }
        if (u.getStatus() != null && u.getStatus() == 0) {
            throw new BizException("账号已停用，请联系管理员");
        }
        SysRole role = roleMapper.selectById(u.getRoleId());
        String roleCode = role == null ? "USER" : role.getRoleCode();
        String scope = role == null ? "SELF" : role.getDataScope();
        u.setLoginFail(0);
        u.setLockUntil(null);
        u.setLastLogin(LocalDateTime.now());
        userMapper.updateById(u);

        String token = jwtUtil.create(u.getId(), u.getRealName(), roleCode, u.getOrgId(), scope);
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", brief(u, roleCode, role.getRoleName()));
        data.put("menus", menus(roleCode, u.getRoleId()));
        return data;
    }

    public Map<String, Object> brief(SysUser u, String roleCode, String roleName) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", u.getId());
        m.put("username", u.getUsername());
        m.put("realName", u.getRealName());
        m.put("avatar", u.getAvatar());
        m.put("phone", u.getPhone());
        m.put("email", u.getEmail());
        m.put("orgId", u.getOrgId());
        m.put("roleCode", roleCode);
        m.put("roleName", roleName);
        m.put("pointId", u.getPointId());
        m.put("driverId", u.getDriverId());
        return m;
    }

    /** 按角色动态获取菜单（仅取 menu_type=M 的菜单，按钮类权限不进入侧边栏） */
    public List<Map<String, Object>> menus(String roleCode, Long roleId) {
        List<SysMenu> all = menuMapper.selectList(new LambdaQueryWrapper<SysMenu>()
                .eq(SysMenu::getVisible, 1)
                .eq(SysMenu::getMenuType, "M")
                .orderByAsc(SysMenu::getSort));
        Set<Long> granted = new HashSet<>();
        if ("ADMIN".equals(roleCode)) {
            all.forEach(m -> granted.add(m.getId()));
        } else {
            roleMenuMapper.selectList(new LambdaQueryWrapper<SysRoleMenu>().eq(SysRoleMenu::getRoleId, roleId))
                    .forEach(rm -> granted.add(rm.getMenuId()));
        }
        List<SysMenu> visible = all.stream().filter(m -> granted.contains(m.getId())).toList();
        List<Map<String, Object>> tree = new ArrayList<>();
        for (SysMenu m : visible) {
            if (m.getParentId() == null || m.getParentId() == 0) {
                Map<String, Object> node = node(m);
                List<Map<String, Object>> children = new ArrayList<>();
                for (SysMenu c : visible) {
                    if (m.getId().equals(c.getParentId())) children.add(node(c));
                }
                node.put("children", children);
                tree.add(node);
            }
        }
        return tree;
    }

    private Map<String, Object> node(SysMenu m) {
        Map<String, Object> n = new LinkedHashMap<>();
        n.put("id", m.getId());
        n.put("name", m.getMenuName());
        n.put("path", m.getPath());
        n.put("icon", m.getIcon());
        n.put("type", m.getMenuType());
        return n;
    }

    public SysUser current() {
        SysUser u = userMapper.selectById(UserContext.userId());
        if (u == null) throw new BizException(401, "登录已过期，请重新登录");
        return u;
    }

    public Map<String, Object> me() {
        SysUser u = current();
        SysRole role = roleMapper.selectById(u.getRoleId());
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("user", brief(u, role == null ? "" : role.getRoleCode(), role == null ? "" : role.getRoleName()));
        data.put("menus", menus(role == null ? "" : role.getRoleCode(), u.getRoleId()));
        return data;
    }

    public void updateProfile(String realName, String phone, String email, String avatar) {
        SysUser u = current();
        if (realName != null && !realName.isBlank()) u.setRealName(realName);
        if (phone != null) u.setPhone(phone);
        if (email != null) u.setEmail(email);
        if (avatar != null && !avatar.isBlank()) u.setAvatar(avatar);
        userMapper.updateById(u);
    }

    public void changePassword(String oldPwd, String newPwd) {
        SysUser u = current();
        if (!encoder.matches(oldPwd, u.getPassword())) throw new BizException("原密码不正确");
        if (newPwd == null || newPwd.length() < 6) throw new BizException("新密码不少于 6 位");
        u.setPassword(encoder.encode(newPwd));
        userMapper.updateById(u);
    }
}
