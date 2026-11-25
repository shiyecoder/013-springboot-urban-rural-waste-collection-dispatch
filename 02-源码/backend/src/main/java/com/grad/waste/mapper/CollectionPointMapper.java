package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.CollectionPoint;
import org.apache.ibatis.annotations.Mapper;

/** 垃圾收集点 Mapper */
@Mapper
public interface CollectionPointMapper extends BaseMapper<CollectionPoint> {
}
