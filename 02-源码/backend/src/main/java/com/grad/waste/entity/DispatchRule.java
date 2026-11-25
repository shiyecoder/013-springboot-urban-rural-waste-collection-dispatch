package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 调度规则版本（表 dispatch_rule）
 */
@Data
@TableName("dispatch_rule")
public class DispatchRule {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String ruleName;

    /**  */
    private Integer version;

    /** 满载度权重 */
    private Integer wLoad;

    /** 滞留时长权重 */
    private Integer wStay;

    /** 投诉次数权重 */
    private Integer wComplaint;

    /** 车辆剩余容量权重 */
    private Integer wCapacity;

    /** 点位距离权重 */
    private Integer wDistance;

    /** 垃圾类型匹配权重 */
    private Integer wTypeMatch;

    /**  */
    private Integer thresholdP1;

    /**  */
    private Integer thresholdP2;

    /**  */
    private Integer thresholdP3;

    /** 净重复核阈值 % */
    private Integer reviewThreshold;

    /**  */
    private Integer enabled;

    /**  */
    private LocalDateTime effectiveTime;

    /**  */
    private String createBy;

    /**  */
    private LocalDateTime createTime;
}
