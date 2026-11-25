package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 用户（表 sys_user）
 */
@Data
@TableName("sys_user")
public class SysUser {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String username;

    /** BCrypt */
    private String password;

    /**  */
    private String realName;

    /** 头像相对路径 */
    private String avatar;

    /**  */
    private String phone;

    /**  */
    private String email;

    /**  */
    private Long orgId;

    /**  */
    private Long roleId;

    /** 收集点管理员绑定点位 */
    private Long pointId;

    /** 司机账号绑定司机档案 */
    private Long driverId;

    /**  */
    private Integer status;

    /** 连续登录失败次数 */
    private Integer loginFail;

    /** 锁定截止时间 */
    private LocalDateTime lockUntil;

    /**  */
    private LocalDateTime lastLogin;

    /**  */
    private LocalDateTime createTime;

    /**  */
    private LocalDateTime updateTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
