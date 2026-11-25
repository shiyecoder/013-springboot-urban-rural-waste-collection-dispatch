package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.ExceptionRecord;
import org.apache.ibatis.annotations.Mapper;

/** 异常记录 Mapper */
@Mapper
public interface ExceptionRecordMapper extends BaseMapper<ExceptionRecord> {
}
