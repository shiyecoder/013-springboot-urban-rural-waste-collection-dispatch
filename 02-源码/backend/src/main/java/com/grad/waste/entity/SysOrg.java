package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 责任单位（表 sys_org）
 */
@Data
@TableName("sys_org")
public class SysOrg {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /** 单位名称 */
    private String orgName;

    /** 类型：环卫所/物业/园区/乡镇 */
    private String orgType;

    /** 所属区域 */
    private String area;

    /** 负责人 */
    private String leader;

    /** 联系电话 */
    private String phone;

    /**  */
    private Integer sort;

    /** 1 正常 0 停用 */
    private Integer status;

    /**  */
    private LocalDateTime createTime;

    @TableLogic
    /**  */
    private Integer deleted;
}
