package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 临时报满（表 overflow_report）
 */
@Data
@TableName("overflow_report")
public class OverflowReport {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String reportNo;

    /**  */
    private Long pointId;

    /** LIGHT/OBVIOUS/SERIOUS */
    private String overflowLevel;

    /**  */
    private BigDecimal estimatedWeight;

    /** 现场图片相对路径 */
    private String image;

    /**  */
    private String description;

    /** 紧急度（含满载度与滞留） */
    private BigDecimal urgencyScore;

    /**  */
    private Long reporterId;

    /**  */
    private LocalDateTime reportTime;

    /** PENDING/DISPATCHED/DONE/CANCELED */
    private String status;

    /**  */
    private Long orderId;

    /**  */
    private LocalDateTime createTime;
}
