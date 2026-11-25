package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.Vehicle;
import org.apache.ibatis.annotations.Mapper;

/** 清运车辆 Mapper */
@Mapper
public interface VehicleMapper extends BaseMapper<Vehicle> {
}
