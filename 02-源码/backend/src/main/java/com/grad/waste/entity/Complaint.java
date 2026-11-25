package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 投诉记录（表 complaint）
 */
@Data
@TableName("complaint")
public class Complaint {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /**  */
    private Long pointId;

    /**  */
    private String content;

    /** LOW/MID/HIGH */
    private String level;

    /**  */
    private String source;

    /** PENDING/DONE */
    private String handleStatus;

    /**  */
    private LocalDateTime happenTime;

    /**  */
    private LocalDateTime createTime;
}
