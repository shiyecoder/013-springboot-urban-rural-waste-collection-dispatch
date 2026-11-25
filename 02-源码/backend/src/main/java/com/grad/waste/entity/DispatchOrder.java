package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 清运任务（表 dispatch_order）
 */
@Data
@TableName("dispatch_order")
public class DispatchOrder {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String orderNo;

    /** PLAN 周期 / URGENT 紧急 / MERGE 合并 */
    private String orderType;

    /**  */
    private Long routeId;

    /**  */
    private Long vehicleId;

    /**  */
    private Long driverId;

    /**  */
    private Long disposeSiteId;

    /** 合并点摘要 */
    private String pointSummary;

    /**  */
    private Integer stopCount;

    /** 计划到场时间 */
    private LocalDateTime planTime;

    /** 实际派单时间 */
    private LocalDateTime dispatchTime;

    /** 预估总重 */
    private BigDecimal estimatedWeight;

    /** 各点实际合计 */
    private BigDecimal actualWeight;

    /** PENDING_DISPATCH 待派车/ACCEPTED 已接单/RUNNING 清运中/PENDING_CONFIRM 待确认/DONE 已完成/CANCELED 已取消/ABNORMAL 异常 */
    private String status;

    /** 联合调度得分 */
    private BigDecimal priorityScore;

    /** P1/P2/P3/NONE */
    private String priorityGrade;

    /**  */
    private Long dispatcherId;

    /** 取消/改派/拒接原因 */
    private String reason;

    /**  */
    private Long createBy;

    /**  */
    private LocalDateTime createTime;

    /**  */
    private LocalDateTime updateTime;

    /**  */
    private Integer version;

    @TableLogic
    /**  */
    private Integer deleted;
}
