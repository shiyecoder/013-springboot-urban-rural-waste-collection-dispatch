package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 站内消息（表 sys_message）
 */
@Data
@TableName("sys_message")
public class SysMessage {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private String title;

    /**  */
    private String content;

    /** 业务类型 */
    private String bizType;

    /** 业务编号，用于详情跳转 */
    private String bizNo;

    /**  */
    private Long receiverId;

    /**  */
    private Integer readFlag;

    /**  */
    private LocalDateTime createTime;
}
