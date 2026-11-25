package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.CollectionPlan;
import org.apache.ibatis.annotations.Mapper;

/** 周期清运计划 Mapper */
@Mapper
public interface CollectionPlanMapper extends BaseMapper<CollectionPlan> {
}
