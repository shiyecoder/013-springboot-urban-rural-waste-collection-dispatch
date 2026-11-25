package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;


/**
 * 字典（表 sys_dict）
 */
@Data
@TableName("sys_dict")
public class SysDict {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String dictType;

    /**  */
    private String dictLabel;

    /**  */
    private String dictValue;

    /**  */
    private Integer sort;

    /**  */
    private Integer status;
}
