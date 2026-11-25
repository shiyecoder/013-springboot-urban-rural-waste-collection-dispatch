package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 操作日志（表 sys_log）
 */
@Data
@TableName("sys_log")
public class SysLog {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private Long userId;

    /**  */
    private String userName;

    /**  */
    private String module;

    /**  */
    private String action;

    /**  */
    private String method;

    /**  */
    private String params;

    /**  */
    private String ip;

    /**  */
    private Integer costMs;

    /**  */
    private LocalDateTime createTime;
}
