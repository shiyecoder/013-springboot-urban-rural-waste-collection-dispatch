package com.grad.waste.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.grad.waste.common.BizException;
import com.grad.waste.common.UserContext;
import com.grad.waste.entity.*;
import com.grad.waste.mapper.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

/**
 * 清运任务核心服务。
 * 状态机：待派车 → 已接单 → 清运中 → 待确认 → 已完成；
 * 取消 / 拒接 / 终止 / 改派必须填写原因（≥5 字）；派单校验载重与司机时间冲突。
 */
@Service
public class DispatchService {

    private static final Map<String, String> FLOW = new LinkedHashMap<>();
    static {
        FLOW.put("PENDING_DISPATCH", "ACCEPTED");
        FLOW.put("ACCEPTED", "RUNNING");
        FLOW.put("RUNNING", "PENDING_CONFIRM");
        FLOW.put("PENDING_CONFIRM", "DONE");
    }

    private final DispatchOrderMapper orderMapper;
    private final RouteStopMapper stopMapper;
    private final VehicleMapper vehicleMapper;
    private final DriverMapper driverMapper;
    private final FlowLogMapper flowMapper;
    private final DispatchScoreMapper scoreMapper;
    private final WeighingRecordMapper weighMapper;
    private final SysMessageMapper msgMapper;
    private final ScoreService scoreService;

    public DispatchService(DispatchOrderMapper orderMapper, RouteStopMapper stopMapper,
                           VehicleMapper vehicleMapper, DriverMapper driverMapper, FlowLogMapper flowMapper,
                           DispatchScoreMapper scoreMapper, WeighingRecordMapper weighMapper,
                           SysMessageMapper msgMapper, ScoreService scoreService) {
        this.orderMapper = orderMapper;
        this.stopMapper = stopMapper;
        this.vehicleMapper = vehicleMapper;
        this.driverMapper = driverMapper;
        this.flowMapper = flowMapper;
        this.scoreMapper = scoreMapper;
        this.weighMapper = weighMapper;
        this.msgMapper = msgMapper;
        this.scoreService = scoreService;
    }

    /** 派车 / 改派：载重、车况、保养、司机时间冲突全部后端校验 */
    @Transactional
    public void assign(Long id, Long vehicleId, Long driverId, Long siteId, LocalDateTime planTime,
                       boolean reassign, String reason) {
        DispatchOrder o = mustGet(id);
        if (!"PENDING_DISPATCH".equals(o.getStatus()) && !reassign) {
            throw new BizException("当前状态不允许派车：" + o.getStatus());
        }
        if (reassign && !List.of("ACCEPTED", "RUNNING").contains(o.getStatus())) {
            throw new BizException("仅已接单或清运中的任务可以改派");
        }
        if (reassign && (reason == null || reason.trim().length() < 5)) {
            throw new BizException("改派必须填写原因，且不少于 5 个字");
        }
        Vehicle v = vehicleMapper.selectById(vehicleId);
        if (v == null) throw new BizException("车辆不存在");
        if ("MAINTAIN".equals(v.getStatus())) throw new BizException("车辆保养中，不可派单");
        if ("DISABLED".equals(v.getStatus())) throw new BizException("车辆已停用");
        // 硬性规则 3：预估重量不得超过车辆载重
        if (v.getLoadCapacity().compareTo(o.getEstimatedWeight()) < 0) {
            throw new BizException("预估重量 " + o.getEstimatedWeight() + " 吨超过车辆载重 "
                    + v.getLoadCapacity() + " 吨，请更换车辆或拆分任务");
        }
        Driver d = driverMapper.selectById(driverId);
        if (d == null) throw new BizException("司机不存在");
        if (d.getStatus() != null && d.getStatus() == 0) throw new BizException("司机处于离岗状态");
        // 司机时间冲突：同一司机前后 2 小时内不得有其它进行中任务
        LocalDateTime pt = planTime == null ? o.getPlanTime() : planTime;
        List<DispatchOrder> conflict = orderMapper.selectList(new LambdaQueryWrapper<DispatchOrder>()
                .eq(DispatchOrder::getDriverId, driverId)
                .in(DispatchOrder::getStatus, "ACCEPTED", "RUNNING")
                .ne(DispatchOrder::getId, id));
        for (DispatchOrder c : conflict) {
            if (c.getPlanTime() != null && Math.abs(java.time.Duration.between(c.getPlanTime(), pt).toMinutes()) < 120) {
                throw new BizException("司机在该时段已有任务 " + c.getOrderNo() + "，存在时间冲突");
            }
        }
        if (o.getVehicleId() != null && o.getDriverId() != null && reassign) {
            flow(o, o.getStatus(), o.getStatus(), "改派", "原司机 " + driverMapper.selectById(o.getDriverId()).getName() + "：" + reason);
        }
        o.setVehicleId(vehicleId);
        o.setDriverId(driverId);
        o.setDisposeSiteId(siteId);
        o.setPlanTime(pt);
        o.setDispatchTime(LocalDateTime.now());
        o.setDispatcherId(2L);
        o.setStatus("ACCEPTED");
        o.setVersion((o.getVersion() == null ? 0 : o.getVersion()) + 1);
        orderMapper.updateById(o);
        v.setStatus("BUSY");
        vehicleMapper.updateById(v);

        flow(o, reassign ? o.getStatus() : "PENDING_DISPATCH", "ACCEPTED", reassign ? "改派" : "派车",
                reassign ? reason : "调度员 " + UserContext.name() + " 派车");
        message("任务已派发", "您有新任务 " + o.getOrderNo() + "，计划 "
                + pt + " 到场", "DISPATCH", o.getOrderNo());
    }

    /** 状态流转：接单 / 开始 / 完成各点 / 确认交接 / 取消 / 拒接 */
    @Transactional
    public void transition(Long id, String action, String reason) {
        DispatchOrder o = mustGet(id);
        String target;
        String actName;
        switch (action) {
            case "accept" -> { target = "ACCEPTED"; actName = "司机接单"; }
            case "start" -> { target = "RUNNING"; actName = "开始清运"; }
            case "finish" -> { target = "PENDING_CONFIRM"; actName = "完成各点清运"; }
            case "confirm" -> { target = "DONE"; actName = "确认交接"; }
            case "cancel" -> { target = "CANCELED"; actName = "取消任务"; }
            case "refuse" -> { target = "PENDING_DISPATCH"; actName = "司机拒接"; }
            default -> throw new BizException("不支持的操作：" + action);
        }
        if (List.of("cancel", "refuse").contains(action)
                && (reason == null || reason.trim().length() < 5)) {
            throw new BizException("取消或拒接必须填写原因，且不少于 5 个字");
        }
        if (!List.of("cancel", "refuse").contains(action)) {
            String expect = FLOW.get(o.getStatus());
            if (expect == null || !expect.equals(target)) {
                throw new BizException("当前状态 " + o.getStatus() + " 不允许执行该操作，禁止越级流转");
            }
        }
        String from = o.getStatus();
        o.setStatus(target);
        if (List.of("cancel", "refuse").contains(action)) o.setReason(reason);
        o.setVersion((o.getVersion() == null ? 0 : o.getVersion()) + 1);
        orderMapper.updateById(o);
        flow(o, from, target, actName, reason);
    }

    /** 详情：基础 + 站点 + 计算留痕 + 流转 + 称重 */
    public Map<String, Object> detail(Long id) {
        DispatchOrder o = mustGet(id);
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("order", o);
        m.put("vehicle", o.getVehicleId() == null ? null : vehicleMapper.selectById(o.getVehicleId()));
        m.put("driver", o.getDriverId() == null ? null : driverMapper.selectById(o.getDriverId()));
        m.put("stops", stopMapper.selectList(new LambdaQueryWrapper<RouteStop>()
                .eq(RouteStop::getOrderId, id).orderByAsc(RouteStop::getSeq)));
        m.put("flows", flowMapper.selectList(new LambdaQueryWrapper<FlowLog>()
                .eq(FlowLog::getBizType, "DISPATCH").eq(FlowLog::getBizId, id)
                .orderByAsc(FlowLog::getCreateTime)));
        m.put("scores", scoreMapper.selectList(new LambdaQueryWrapper<DispatchScore>()
                .eq(DispatchScore::getOrderId, id).orderByDesc(DispatchScore::getId)));
        m.put("weighing", weighMapper.selectOne(new LambdaQueryWrapper<WeighingRecord>()
                .eq(WeighingRecord::getOrderId, id).orderByDesc(WeighingRecord::getId).last("limit 1")));
        return m;
    }

    /** 人工调整：原始计算结果不覆盖，仅新增调整记录 */
    @Transactional
    public void adjust(Long id, String reason, Long vehicleId) {
        if (reason == null || reason.trim().length() < 5) throw new BizException("人工调整必须填写原因，且不少于 5 个字");
        DispatchOrder o = mustGet(id);
        DispatchScore latest = scoreMapper.selectOne(new LambdaQueryWrapper<DispatchScore>()
                .eq(DispatchScore::getOrderId, id).orderByDesc(DispatchScore::getId).last("limit 1"));
        if (latest != null) {
            latest.setManualAdjust(1);
            latest.setAdopted(0);
            latest.setAdjustReason(reason);
            scoreMapper.updateById(latest);
        }
        if (vehicleId != null) o.setVehicleId(vehicleId);
        orderMapper.updateById(o);
        flow(o, o.getStatus(), o.getStatus(), "人工调整", reason);
    }

    private DispatchOrder mustGet(Long id) {
        DispatchOrder o = orderMapper.selectById(id);
        if (o == null) throw new BizException("任务不存在或已删除");
        return o;
    }

    private void flow(DispatchOrder o, String from, String to, String action, String reason) {
        FlowLog f = new FlowLog();
        f.setBizType("DISPATCH");
        f.setBizId(o.getId());
        f.setBizNo(o.getOrderNo());
        f.setFromStatus(from);
        f.setToStatus(to);
        f.setAction(action);
        f.setReason(reason);
        f.setOperator(UserContext.name());
        f.setCreateTime(LocalDateTime.now());
        flowMapper.insert(f);
    }

    private void message(String title, String content, String type, String no) {
        SysMessage m = new SysMessage();
        m.setTitle(title);
        m.setContent(content);
        m.setBizType(type);
        m.setBizNo(no);
        m.setReceiverId(7L);
        m.setReadFlag(0);
        m.setCreateTime(LocalDateTime.now());
        msgMapper.insert(m);
    }
}
