package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 异常记录（表 exception_record）
 */
@Data
@TableName("exception_record")
public class ExceptionRecord {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String exceptionNo;

    /**  */
    private Long orderId;

    /**  */
    private Long pointId;

    /** VEHICLE_FAULT/UNREACHABLE/OVERLOAD/MISS_STOP/OTHER */
    private String type;

    /** LOW/MID/HIGH */
    private String level;

    /**  */
    private String description;

    /**  */
    private String image;

    /**  */
    private String reporter;

    /**  */
    private String handler;

    /** 处理结论（改派/恢复/终止） */
    private String handleResult;

    /** OPEN/HANDLING/CLOSED */
    private String status;

    /**  */
    private LocalDateTime createTime;

    /**  */
    private LocalDateTime updateTime;
}
