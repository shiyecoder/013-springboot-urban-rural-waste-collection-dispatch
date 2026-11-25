package com.grad.waste.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.grad.waste.common.BizException;
import com.grad.waste.common.PageResult;
import com.grad.waste.common.R;
import com.grad.waste.entity.*;
import com.grad.waste.mapper.*;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/** 收集点档案：分页、详情、增改删、下拉、区域汇总 */
@RestController
@RequestMapping("/api/point")
public class PointController {

    private final CollectionPointMapper mapper;
    private final CollectionPlanMapper planMapper;
    private final RouteStopMapper stopMapper;

    public PointController(CollectionPointMapper mapper, CollectionPlanMapper planMapper, RouteStopMapper stopMapper) {
        this.mapper = mapper;
        this.planMapper = planMapper;
        this.stopMapper = stopMapper;
    }

    @GetMapping("/page")
    public R<PageResult<CollectionPoint>> page(@RequestParam(defaultValue = "1") long page,
                                               @RequestParam(defaultValue = "10") long size,
                                               @RequestParam(required = false) String kw,
                                               @RequestParam(required = false) String area,
                                               @RequestParam(required = false) String wasteType,
                                               @RequestParam(required = false) String status,
                                               @RequestParam(required = false) Integer loadMin,
                                               @RequestParam(required = false) Integer loadMax) {
        LambdaQueryWrapper<CollectionPoint> w = new LambdaQueryWrapper<>();
        if (kw != null && !kw.isBlank()) {
            w.and(x -> x.like(CollectionPoint::getPointName, kw).or().like(CollectionPoint::getPointCode, kw));
        }
        if (area != null && !area.isBlank()) w.eq(CollectionPoint::getArea, area);
        if (wasteType != null && !wasteType.isBlank()) w.eq(CollectionPoint::getWasteType, wasteType);
        if (status != null && !status.isBlank()) w.eq(CollectionPoint::getStatus, status);
        if (loadMin != null) w.ge(CollectionPoint::getLoadRate, loadMin);
        if (loadMax != null) w.le(CollectionPoint::getLoadRate, loadMax);
        w.orderByDesc(CollectionPoint::getLoadRate).orderByDesc(CollectionPoint::getUpdateTime);
        Page<CollectionPoint> p = mapper.selectPage(new Page<>(page, size), w);
        return R.ok(new PageResult<>(p.getTotal(), p.getCurrent(), p.getSize(), p.getRecords()));
    }

    @GetMapping("/options")
    public R<List<CollectionPoint>> options() {
        return R.ok(mapper.selectList(new LambdaQueryWrapper<CollectionPoint>()
                .eq(CollectionPoint::getStatus, "NORMAL")
                .or().eq(CollectionPoint::getStatus, "OVERFLOW")
                .orderByAsc(CollectionPoint::getPointCode)));
    }

    @GetMapping("/areas")
    public R<List<String>> areas() {
        List<String> areas = new ArrayList<>();
        mapper.selectList(null).forEach(p -> { if (!areas.contains(p.getArea())) areas.add(p.getArea()); });
        return R.ok(areas);
    }

    @GetMapping("/{id}")
    public R<CollectionPoint> get(@PathVariable Long id) {
        CollectionPoint p = mapper.selectById(id);
        if (p == null) throw new BizException("收集点不存在或已删除");
        return R.ok(p);
    }

    @PostMapping
    public R<CollectionPoint> add(@RequestBody CollectionPoint p) {
        validate(p, null);
        // 满载度由后端计算，前端传值不采信
        p.setLoadRate(calcRate(p));
        if (p.getStatus() == null) p.setStatus("NORMAL");
        mapper.insert(p);
        return R.ok(p);
    }

    @PutMapping("/{id}")
    public R<CollectionPoint> update(@PathVariable Long id, @RequestBody CollectionPoint p) {
        CollectionPoint old = mapper.selectById(id);
        if (old == null) throw new BizException("收集点不存在或已删除");
        if (p.getVersion() != null && old.getVersion() != null && !p.getVersion().equals(old.getVersion())) {
            throw new BizException("该记录已被他人更新，请刷新后重试");
        }
        p.setId(id);
        p.setPointCode(old.getPointCode());
        p.setLoadRate(calcRate(p));
        p.setVersion((old.getVersion() == null ? 0 : old.getVersion()) + 1);
        mapper.updateById(p);
        return R.ok(p);
    }

    @DeleteMapping("/{id}")
    public R<Void> delete(@PathVariable Long id) {
        Long plans = planMapper.selectCount(new LambdaQueryWrapper<CollectionPlan>().eq(CollectionPlan::getPointId, id));
        if (plans > 0) throw new BizException("该收集点已被周期计划引用，不能删除，请先停用");
        mapper.deleteById(id);
        return R.ok();
    }

    private void validate(CollectionPoint p, Long id) {
        if (p.getPointCode() == null || p.getPointCode().isBlank()) throw new BizException("点位编码必填");
        p.setPointCode(p.getPointCode().trim());
        if (p.getPointCode().length() > 50) throw new BizException("点位编码长度不能超过 50 个字符");
        if (p.getPointName() == null || p.getPointName().isBlank()) throw new BizException("点位名称必填");
        if (p.getArea() == null || p.getArea().isBlank()) throw new BizException("所属区域必填");
        if (p.getCapacity() == null || p.getCapacity().doubleValue() < 0) throw new BizException("容量不得为负数");
        Long dup = mapper.selectCount(new LambdaQueryWrapper<CollectionPoint>()
                .eq(CollectionPoint::getPointCode, p.getPointCode())
                .ne(id != null, CollectionPoint::getId, id));
        if (dup > 0) throw new BizException("点位编码已存在，请更换");
    }

    private Integer calcRate(CollectionPoint p) {
        if (p.getCapacity() == null || p.getCapacity().doubleValue() <= 0) return 0;
        double load = p.getCurrentLoad() == null ? 0 : p.getCurrentLoad().doubleValue();
        return (int) Math.min(100, Math.round(load / p.getCapacity().doubleValue() * 100));
    }
}
