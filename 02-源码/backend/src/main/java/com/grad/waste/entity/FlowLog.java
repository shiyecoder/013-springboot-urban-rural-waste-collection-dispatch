package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 业务流转日志（表 flow_log）
 */
@Data
@TableName("flow_log")
public class FlowLog {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String bizType;

    /**  */
    private Long bizId;

    /**  */
    private String bizNo;

    /**  */
    private String fromStatus;

    /**  */
    private String toStatus;

    /** 创建/派车/接单/到场/完成/交接/取消/改派/复核 */
    private String action;

    /**  */
    private String reason;

    /**  */
    private String operator;

    /**  */
    private LocalDateTime createTime;
}
