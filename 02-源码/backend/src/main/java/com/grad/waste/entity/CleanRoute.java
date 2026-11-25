package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 清运线路（表 route）
 */
@Data
@TableName("route")
public class CleanRoute {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String routeCode;

    /**  */
    private String routeName;

    /**  */
    private String area;

    /** 线路里程 */
    private BigDecimal distanceKm;

    /**  */
    private Integer stopCount;

    /**  */
    private Integer status;

    /**  */
    private String remark;

    /**  */
    private LocalDateTime createTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
