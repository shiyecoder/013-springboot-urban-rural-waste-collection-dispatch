package com.grad.waste.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.grad.waste.entity.Complaint;
import org.apache.ibatis.annotations.Mapper;

/** 投诉记录 Mapper */
@Mapper
public interface ComplaintMapper extends BaseMapper<Complaint> {
}
