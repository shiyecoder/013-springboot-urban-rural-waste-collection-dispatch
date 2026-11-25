package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 周期清运计划（表 collection_plan）
 */
@Data
@TableName("collection_plan")
public class CollectionPlan {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String planCode;

    /**  */
    private Long pointId;

    /**  */
    private Long routeId;

    /**  */
    private String wasteType;

    /** DAILY/EVERY_2_DAYS/WEEKLY */
    private String frequency;

    /** WEEKLY 时的星期 1-7 */
    private Integer weekday;

    /**  */
    private BigDecimal estimatedWeight;

    /**  */
    private LocalDate nextDate;

    /** ON/OFF */
    private String status;

    /**  */
    private LocalDateTime createTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
