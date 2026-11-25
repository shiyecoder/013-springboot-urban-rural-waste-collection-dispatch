package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.WeighingRecord;
import com.grad.waste.mapper.WeighingRecordMapper;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 称重交接管理：服务端分页、条件查询、增删改。
 */
@RestController
@RequestMapping("/api/weighing")
public class WeighingController {

    private final WeighingRecordMapper mapper;

    public WeighingController(WeighingRecordMapper mapper) {
        this.mapper = mapper;
    }

    @GetMapping("/page")
    public R<PageResult<WeighingRecord>> page(@RequestParam(defaultValue = "1") long page,
                                        @RequestParam(defaultValue = "10") long size,
                                        @RequestParam(required = false) String kw,
                                        @RequestParam(required = false) String status) {
        QueryWrapper<WeighingRecord> w = new QueryWrapper<>();
            if (kw != null && !kw.isBlank()) {
                w.and(x -> x.like("record_no", kw));
            }
            if (status != null && !status.isBlank()) w.eq("review_status", status);
        w.orderByDesc("id");
        Page<WeighingRecord> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<WeighingRecord>> options() {
        return R.ok(mapper.selectList(new QueryWrapper<WeighingRecord>().orderByAsc("id")));
    }

    @GetMapping("/{id}")
    public R<WeighingRecord> get(@PathVariable Long id) {
        WeighingRecord o = mapper.selectById(id);
        if (o == null) throw new BizException("记录不存在或已删除");
        return R.ok(o);
    }

    @PostMapping
    public R<WeighingRecord> add(@RequestBody WeighingRecord o) {
        mapper.insert(o);
        return R.ok(o);
    }

    @PutMapping("/{id}")
    public R<WeighingRecord> update(@PathVariable Long id, @RequestBody WeighingRecord o) {
        if (mapper.selectById(id) == null) throw new BizException("记录不存在或已删除");
        mapper.updateById(o);
        return R.ok(o);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        mapper.deleteById(id);
        return R.ok();
    }
}
