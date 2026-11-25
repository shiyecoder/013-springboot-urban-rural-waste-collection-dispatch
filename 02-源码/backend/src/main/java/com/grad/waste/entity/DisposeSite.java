package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 处置场（表 dispose_site）
 */
@Data
@TableName("dispose_site")
public class DisposeSite {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String siteCode;

    /**  */
    private String siteName;

    /**  */
    private String address;

    /** 日处理能力(吨) */
    private BigDecimal capacity;

    /** 可接收垃圾类型，逗号分隔 */
    private String disposeTypes;

    /**  */
    private String manager;

    /**  */
    private String phone;

    /**  */
    private String image;

    /** 1 启用 0 停用 */
    private Integer status;

    /**  */
    private LocalDateTime createTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
