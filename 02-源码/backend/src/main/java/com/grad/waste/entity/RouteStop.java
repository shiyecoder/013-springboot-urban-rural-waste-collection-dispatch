package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 任务站点（表 route_stop）
 */
@Data
@TableName("route_stop")
public class RouteStop {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private Long orderId;

    /**  */
    private Long pointId;

    /** 站点顺序 */
    private Integer seq;

    /**  */
    private LocalDateTime planArrive;

    /** 实际到场 */
    private LocalDateTime arriveTime;

    /** 实际离场 */
    private LocalDateTime leaveTime;

    /**  */
    private BigDecimal estimatedWeight;

    /**  */
    private BigDecimal actualWeight;

    /** 现场图片 */
    private String siteImage;

    /** WAITING/ARRIVED/DONE/SKIPPED */
    private String status;

    /**  */
    private String remark;
}
