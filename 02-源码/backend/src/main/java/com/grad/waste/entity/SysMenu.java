package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 菜单（表 sys_menu）
 */
@Data
@TableName("sys_menu")
public class SysMenu {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private Long parentId;

    /**  */
    private String menuName;

    /** 前端路由 */
    private String path;

    /**  */
    private String icon;

    /** M 菜单 B 按钮 */
    private String menuType;

    /** 权限标识 */
    private String perm;

    /**  */
    private Integer sort;

    /** 1 显示 0 隐藏（菜单管理项自身隐藏） */
    private Integer visible;

    /**  */
    private LocalDateTime createTime;
}
