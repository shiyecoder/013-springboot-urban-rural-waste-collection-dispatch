package com.grad.waste.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.TableLogic;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 附件（表 attachment）
 */
@Data
@TableName("attachment")
public class Attachment {

    @TableId(type = IdType.AUTO)
    /**  */
    private Long id;

    /** 业务类型 */
    private String bizType;

    /**  */
    private Long bizId;

    /**  */
    private String fileName;

    /** 相对路径，不存外部 URL */
    private String filePath;

    /**  */
    private Long fileSize;

    /**  */
    private String uploader;

    /**  */
    private LocalDateTime createTime;
}
