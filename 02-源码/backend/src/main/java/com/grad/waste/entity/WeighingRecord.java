package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 处置称重交接（表 weighing_record）
 */
@Data
@TableName("weighing_record")
public class WeighingRecord {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String recordNo;

    /**  */
    private Long orderId;

    /**  */
    private Long disposeSiteId;

    /** 进场重量(吨) */
    private BigDecimal inWeight;

    /** 出场重量(吨) */
    private BigDecimal outWeight;

    /** 净重=进-出 */
    private BigDecimal netWeight;

    /** 填埋/焚烧发电/资源化利用 */
    private String disposeType;

    /** 称重单图片 */
    private String weighingImage;

    /**  */
    private LocalDateTime weighTime;

    /** 净重与各点合计偏差 % */
    private BigDecimal deviation;

    /** PASS/REVIEW 复核 */
    private String reviewStatus;

    /**  */
    private String reviewNote;

    /**  */
    private String reviewer;

    /**  */
    private LocalDateTime createTime;
}
