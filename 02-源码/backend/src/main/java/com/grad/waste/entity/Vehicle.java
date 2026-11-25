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
 * 清运车辆（表 vehicle）
 */
@Data
@TableName("vehicle")
public class Vehicle {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String plateNo;

    /** 压缩式/后装式/密闭罐式/勾臂式 */
    private String vehicleType;

    /** 载重(吨) */
    private BigDecimal loadCapacity;

    /** 可收运类型 */
    private String wasteTypes;

    /**  */
    private LocalDate annualCheckDate;

    /** 累计里程 km */
    private Integer mileage;

    /** IDLE/BUSY/MAINTAIN/DISABLED */
    private String status;

    /**  */
    private String image;

    /**  */
    private String remark;

    /**  */
    private LocalDateTime createTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
