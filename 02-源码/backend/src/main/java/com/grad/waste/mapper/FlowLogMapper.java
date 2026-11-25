package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.FlowLog;
import org.apache.ibatis.annotations.Mapper;

/** 业务流转日志 Mapper */
@Mapper
public interface FlowLogMapper extends BaseMapper<FlowLog> {
}
