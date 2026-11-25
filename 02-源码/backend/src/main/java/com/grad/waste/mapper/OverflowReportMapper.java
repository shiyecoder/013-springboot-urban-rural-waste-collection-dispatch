package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.OverflowReport;
import org.apache.ibatis.annotations.Mapper;

/** 临时报满 Mapper */
@Mapper
public interface OverflowReportMapper extends BaseMapper<OverflowReport> {
}
