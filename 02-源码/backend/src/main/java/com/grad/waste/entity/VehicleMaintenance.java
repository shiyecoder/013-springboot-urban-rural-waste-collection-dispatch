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
 * 车辆保养（表 vehicle_maintenance）
 */
@Data
@TableName("vehicle_maintenance")
public class VehicleMaintenance {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private Long vehicleId;

    /** 常规保养/年检/维修 */
    private String maintainType;

    /**  */
    private LocalDate maintainDate;

    /** 保养时里程 */
    private Integer mileage;

    /** 下次保养日期 */
    private LocalDate nextDate;

    /** 下次保养里程 */
    private Integer nextMileage;

    /**  */
    private BigDecimal cost;

    /** DONE/DUE 预警/ING 保养中 */
    private String status;

    /**  */
    private String remark;

    /**  */
    private LocalDateTime createTime;
}
