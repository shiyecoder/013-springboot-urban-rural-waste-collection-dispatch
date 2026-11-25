package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 垃圾收集点（表 collection_point）
 */
@Data
@TableName("collection_point")
public class CollectionPoint {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /** 点位编码，业务唯一 */
    private String pointCode;

    /**  */
    private String pointName;

    /** 所属区域 */
    private String area;

    /**  */
    private String address;

    /** 垃圾类型（字典 waste_type） */
    private String wasteType;

    /** 容量(吨) */
    private BigDecimal capacity;

    /** 当前装载量(吨) */
    private BigDecimal currentLoad;

    /** 当前满载度 %，后端计算 */
    private Integer loadRate;

    /** 责任单位 */
    private Long orgId;

    /** 负责人 */
    private String manager;

    /**  */
    private String managerPhone;

    /**  */
    private LocalDateTime lastClearTime;

    /**  */
    private BigDecimal longitude;

    /**  */
    private BigDecimal latitude;

    /**  */
    private String coverImage;

    /** NORMAL/OVERFLOW/DISABLED */
    private String status;

    /**  */
    private Integer version;

    /**  */
    private LocalDateTime createTime;

    /**  */
    private LocalDateTime updateTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
