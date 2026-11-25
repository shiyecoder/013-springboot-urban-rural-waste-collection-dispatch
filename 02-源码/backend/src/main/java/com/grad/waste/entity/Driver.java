package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 司机档案（表 driver）
 */
@Data
@TableName("driver")
public class Driver {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String driverNo;

    /**  */
    private String name;

    /**  */
    private String phone;

    /** 驾驶证号 */
    private String licenseNo;

    /** 准驾车型 */
    private String licenseType;

    /**  */
    private LocalDate licenseExpire;

    /** 常驾车辆 */
    private Long vehicleId;

    /**  */
    private String avatar;

    /** 1 在岗 0 离岗 */
    private Integer status;

    /**  */
    private LocalDateTime createTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
