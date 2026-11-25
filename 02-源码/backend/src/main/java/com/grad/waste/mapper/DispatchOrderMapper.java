package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.DispatchOrder;
import org.apache.ibatis.annotations.Mapper;

/** 清运任务 Mapper */
@Mapper
public interface DispatchOrderMapper extends BaseMapper<DispatchOrder> {
}
