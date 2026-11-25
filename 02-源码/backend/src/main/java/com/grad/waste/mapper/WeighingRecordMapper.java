package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.WeighingRecord;
import org.apache.ibatis.annotations.Mapper;

/** 处置称重交接 Mapper */
@Mapper
public interface WeighingRecordMapper extends BaseMapper<WeighingRecord> {
}
