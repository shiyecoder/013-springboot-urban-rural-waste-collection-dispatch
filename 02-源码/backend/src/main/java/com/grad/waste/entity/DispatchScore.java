package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 调度计算留痕（表 dispatch_score）
 */
@Data
@TableName("dispatch_score")
public class DispatchScore {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private Long orderId;

    /**  */
    private Long ruleId;

    /**  */
    private Integer ruleVersion;

    /** 输入快照 JSON */
    private String snapshot;

    /**  */
    private BigDecimal vLoad;

    /**  */
    private BigDecimal vStay;

    /**  */
    private Integer vComplaint;

    /**  */
    private BigDecimal vCapacity;

    /**  */
    private BigDecimal vDistance;

    /**  */
    private Integer vTypeMatch;

    /**  */
    private BigDecimal sLoad;

    /**  */
    private BigDecimal sStay;

    /**  */
    private BigDecimal sComplaint;

    /**  */
    private BigDecimal sCapacity;

    /**  */
    private BigDecimal sDistance;

    /**  */
    private BigDecimal sTypeMatch;

    /**  */
    private BigDecimal totalScore;

    /** P1/P2/P3/NONE */
    private String grade;

    /** 主要影响因素 */
    private String factors;

    /** 未满足条件 */
    private String unmet;

    /** 可改进项 */
    private String improve;

    /** 是否采纳推荐 */
    private Integer adopted;

    /** 人工是否调整 */
    private Integer manualAdjust;

    /**  */
    private String adjustReason;

    /**  */
    private LocalDateTime createTime;
}
