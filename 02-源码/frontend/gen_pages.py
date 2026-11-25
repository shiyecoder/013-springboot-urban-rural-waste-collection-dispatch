#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 NEW-013 前端核心业务页面（收集点 / 调度台 / 详情 / 规则 / 报表 / 任务端 / 个人中心）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "frontend/src")
F = {}
def add(rel, c): F[os.path.join(SRC, rel)] = c

add("views/PointList.vue", r"""
<template>
  <div>
    <div class="card"><div class="card-b">
      <div class="filter-bar">
        <el-input v-model="q.kw" placeholder="点位编码 / 名称" clearable @keyup.enter="reload" />
        <el-select v-model="q.area" placeholder="所属区域" clearable>
          <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
        </el-select>
        <el-select v-model="q.wasteType" placeholder="垃圾类型" clearable>
          <el-option v-for="w in WASTE" :key="w" :label="w" :value="w" />
        </el-select>
        <el-select v-model="q.status" placeholder="点位状态" clearable>
          <el-option label="正常" value="NORMAL" /><el-option label="满溢" value="OVERFLOW" />
          <el-option label="停用" value="DISABLED" />
        </el-select>
        <el-button type="primary" @click="reload">查询</el-button>
        <el-button @click="reset">重置</el-button>
        <el-button type="primary" plain style="margin-left:auto" @click="openAdd">
          <el-icon><Plus /></el-icon>新建收集点
        </el-button>
      </div>
    </div></div>

    <div class="card">
      <div class="card-h"><h2>收集点列表</h2>
        <div style="margin-left:auto" class="muted">共 {{ total }} 条</div>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column label="现场" width="96">
          <template #default="{ row }"><img class="thumb" :src="row.coverImage" alt="" /></template>
        </el-table-column>
        <el-table-column prop="pointCode" label="点位编码" min-width="130" />
        <el-table-column label="点位名称" min-width="200">
          <template #default="{ row }">
            {{ row.pointName }}
            <span class="tbl-cell-sub">负责人 {{ row.manager }} · {{ row.managerPhone }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="area" label="所属区域" min-width="110" />
        <el-table-column prop="wasteType" label="垃圾类型" min-width="110" />
        <el-table-column prop="capacity" label="容量(吨)" min-width="100" align="right" />
        <el-table-column label="满载度" min-width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.loadRate" :stroke-width="8"
                         :color="row.loadRate >= 85 ? '#B3261E' : row.loadRate >= 60 ? '#B26B00' : '#2E7D5B'" />
          </template>
        </el-table-column>
        <el-table-column label="最后清运" min-width="170">
          <template #default="{ row }"><span class="num">{{ formatTime(row.lastClearTime) }}</span></template>
        </el-table-column>
        <el-table-column label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，可清空筛选或新建收集点" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:14px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10, 20, 50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-dialog v-model="visible" :title="form.id ? '编辑收集点' : '新建收集点'" width="680px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="点位编码" required>
          <el-input v-model="form.pointCode" :disabled="!!form.id" style="width:260px" />
        </el-form-item>
        <el-form-item label="点位名称" required><el-input v-model="form.pointName" style="width:360px" /></el-form-item>
        <el-form-item label="所属区域" required>
          <el-select v-model="form.area" style="width:200px">
            <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
          </el-select>
        </el-form-item>
        <el-form-item label="垃圾类型" required>
          <el-select v-model="form.wasteType" style="width:200px">
            <el-option v-for="w in WASTE" :key="w" :label="w" :value="w" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量(吨)" required>
          <el-input-number v-model="form.capacity" :precision="2" style="width:200px" />
        </el-form-item>
        <el-form-item label="当前装载量">
          <el-input-number v-model="form.currentLoad" :precision="2" style="width:200px" />
          <span class="muted" style="margin-left:8px">满载度由后端计算</span>
        </el-form-item>
        <el-form-item label="负责人"><el-input v-model="form.manager" style="width:200px" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.managerPhone" style="width:200px" /></el-form-item>
        <el-form-item label="点位状态">
          <el-select v-model="form.status" style="width:200px">
            <el-option label="正常" value="NORMAL" /><el-option label="满溢" value="OVERFLOW" />
            <el-option label="停用" value="DISABLED" />
          </el-select>
        </el-form-item>
        <el-form-item label="现场图片">
          <el-upload :show-file-list="false" :http-request="upload">
            <img v-if="form.coverImage" class="thumb" style="width:120px;height:90px" :src="form.coverImage" alt="" />
            <el-button v-else size="small">上传图片</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const WASTE = ['生活垃圾', '建筑垃圾', '餐厨垃圾', '大件垃圾', '园林绿化']
const q = reactive({ kw: '', area: '', wasteType: '', status: '' })
const rows = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const visible = ref(false)
const areas = ref([])
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/point/page', { params: { page: page.value, size: size.value, ...q } })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function reset() { Object.assign(q, { kw: '', area: '', wasteType: '', status: '' }); reload() }
function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, { status: 'NORMAL', capacity: 5, currentLoad: 0 })
  visible.value = true
}
function openEdit(row) { Object.keys(form).forEach((k) => delete form[k]); Object.assign(form, row); visible.value = true }
async function save() {
  if (form.id) await request.put('/api/point/' + form.id, form)
  else await request.post('/api/point', form)
  ElMessage.success('保存成功'); visible.value = false; load()
}
async function remove(row) {
  await ElMessageBox.confirm('该点位删除后不可恢复，确认删除？', '删除确认', { type: 'warning' })
  await request.delete('/api/point/' + row.id)
  ElMessage.success('已删除'); load()
}
async function upload(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.coverImage = d.path
}
onMounted(async () => { areas.value = await request.get('/api/point/areas'); load() })
</script>
""")

add("views/DispatchConsole.vue", r"""
<template>
  <div>
    <div class="card" style="margin-bottom:0;border-bottom-left-radius:0;border-bottom-right-radius:0">
      <el-tabs v-model="status" @tab-change="reload" style="padding:0 16px">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane v-for="s in TABS" :key="s.value" :name="s.value">
          <template #label>{{ s.label }}<el-badge v-if="s.value === 'PENDING_DISPATCH'" :value="pending" type="warning" /></template>
        </el-tab-pane>
      </el-tabs>
      <div class="card-b" style="padding:8px 20px 16px">
        <div class="filter-bar">
          <el-input v-model="kw" placeholder="任务编号 / 点位" clearable @keyup.enter="reload" />
          <el-date-picker v-model="date" type="date" value-format="YYYY-MM-DD" placeholder="计划日期" />
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
      </div>
    </div>

    <div class="card" style="border-top:none;border-top-left-radius:0;border-top-right-radius:0">
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column prop="orderNo" label="任务编号" min-width="160" />
        <el-table-column label="收集点 / 线路" min-width="240">
          <template #default="{ row }">
            {{ row.pointSummary }}
            <span class="tbl-cell-sub">线路 ID {{ row.routeId }} · {{ row.stopCount }} 个站点</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" min-width="90">
          <template #default="{ row }">
            {{ { PLAN: '周期计划', URGENT: '紧急插单', MERGE: '合并任务' }[row.orderType] || row.orderType }}
          </template>
        </el-table-column>
        <el-table-column prop="estimatedWeight" label="预估重量" min-width="110" align="right" />
        <el-table-column label="优先级" min-width="120">
          <template #default="{ row }">
            <span v-if="row.priorityGrade" class="tag" :class="'tag-' + row.priorityGrade.toLowerCase()">
              {{ row.priorityGrade }} · {{ row.priorityScore }}
            </span>
            <span v-else class="muted">未计算</span>
          </template>
        </el-table-column>
        <el-table-column label="计划时间" min-width="170">
          <template #default="{ row }"><span class="num">{{ formatTime(row.planTime) }}</span></template>
        </el-table-column>
        <el-table-column label="状态" min-width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'PENDING_DISPATCH'" link type="primary" @click="openAssign(row)">派车</el-button>
            <el-button v-if="['ACCEPTED', 'RUNNING'].includes(row.status)" link type="warning" @click="openReassign(row)">改派</el-button>
            <el-button link type="primary" @click="router.push('/dispatch/' + row.id)">详情</el-button>
            <el-button v-if="row.status === 'PENDING_CONFIRM'" link type="success" @click="confirmOrder(row)">确认</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前条件下无任务，可切换状态标签或新建任务" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:14px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10, 20, 50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-drawer v-model="drawer" :title="reassignMode ? '任务改派' : '调度派车'" size="560px">
      <div v-if="cur" class="hint" style="margin-bottom:16px">
        任务 {{ cur.orderNo }} · {{ cur.pointSummary }}<br />
        预估重量 {{ cur.estimatedWeight }} 吨 · 计划 {{ formatTime(cur.planTime) }}
      </div>
      <el-form label-width="100px">
        <el-form-item label="车辆" required>
          <el-select v-model="assignForm.vehicleId" style="width:240px" placeholder="选择车辆">
            <el-option v-for="v in vehicles" :key="v.id" :label="v.plateNo + '（' + v.loadCapacity + ' 吨 · ' + v.vehicleType + '）'"
                       :value="v.id" :disabled="v.status === 'MAINTAIN' || v.status === 'DISABLED'" />
          </el-select>
        </el-form-item>
        <el-form-item label="司机" required>
          <el-select v-model="assignForm.driverId" style="width:240px" placeholder="选择司机">
            <el-option v-for="d in drivers" :key="d.id" :label="d.name + '（' + d.phone + '）'" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="处置场">
          <el-select v-model="assignForm.disposeSiteId" style="width:240px" clearable>
            <el-option v-for="s in sites" :key="s.id" :label="s.siteName" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!reassignMode" label="计划时间">
          <el-date-picker v-model="assignForm.planTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:240px" />
        </el-form-item>
        <el-form-item v-if="reassignMode" label="改派原因" required>
          <el-input v-model="assignForm.reason" type="textarea" :rows="3" placeholder="不少于 5 个字，例如：原定车辆年检到期临时停用" />
        </el-form-item>
      </el-form>
      <div class="hint">
        派单校验：预估重量不得超过车辆载重；司机同一时段不得存在重叠任务；保养中车辆不可派单。以上均由后端校验。
      </div>
      <template #footer>
        <el-button @click="drawer = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitAssign">提交</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const router = useRouter()
const TABS = [
  { label: '待派车', value: 'PENDING_DISPATCH' }, { label: '已接单', value: 'ACCEPTED' },
  { label: '清运中', value: 'RUNNING' }, { label: '待确认', value: 'PENDING_CONFIRM' },
  { label: '已完成', value: 'DONE' }, { label: '异常', value: 'ABNORMAL' }, { label: '已取消', value: 'CANCELED' }
]
const rows = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const status = ref('')
const kw = ref('')
const date = ref('')
const loading = ref(false)
const pending = ref(0)
const drawer = ref(false)
const saving = ref(false)
const reassignMode = ref(false)
const cur = ref(null)
const vehicles = ref([])
const drivers = ref([])
const sites = ref([])
const assignForm = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/dispatch/page', {
      params: { page: page.value, size: size.value, kw: kw.value, status: status.value, date: date.value }
    })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally { loading.value = false }
}
async function loadPending() {
  const d = await request.get('/api/dispatch/page', { params: { page: 1, size: 1, status: 'PENDING_DISPATCH' } })
  pending.value = d.total || 0
}
function reload() { page.value = 1; load(); loadPending() }
function reset() { kw.value = ''; date.value = ''; status.value = ''; reload() }

function openAssign(row) {
  cur.value = row; reassignMode.value = false
  Object.assign(assignForm, { vehicleId: null, driverId: null, disposeSiteId: null, planTime: row.planTime, reason: '' })
  drawer.value = true
}
function openReassign(row) {
  cur.value = row; reassignMode.value = true
  Object.assign(assignForm, { vehicleId: row.vehicleId, driverId: row.driverId, disposeSiteId: row.disposeSiteId, reason: '' })
  drawer.value = true
}
async function submitAssign() {
  if (!assignForm.vehicleId || !assignForm.driverId) { ElMessage.warning('请选择车辆与司机'); return }
  saving.value = true
  try {
    const url = reassignMode.value ? '/api/dispatch/' + cur.value.id + '/reassign' : '/api/dispatch/' + cur.value.id + '/assign'
    await request.post(url, assignForm)
    ElMessage.success(reassignMode.value ? '改派成功' : '派车成功')
    drawer.value = false
    reload()
  } finally { saving.value = false }
}
async function confirmOrder(row) {
  await ElMessageBox.confirm('确认该任务已完成交接？确认后进入已完成状态。', '确认交接', { type: 'info' })
  await request.post('/api/dispatch/' + row.id + '/transition', { action: 'confirm' })
  ElMessage.success('已确认'); reload()
}
onMounted(async () => {
  const [v, d, s] = await Promise.all([
    request.get('/api/vehicle/options'), request.get('/api/driver/options'), request.get('/api/site/options')
  ])
  vehicles.value = v || []; drivers.value = d || []; sites.value = s || []
  load(); loadPending()
})
</script>
""")

add("views/DispatchDetail.vue", r"""
<template>
  <div v-if="d.order">
    <div class="card" style="padding:18px 24px">
      <div style="display:flex;align-items:center;gap:12px">
        <h2 style="margin:0;font-size:18px">{{ d.order.orderNo }}</h2>
        <el-tag :type="statusType(d.order.status)" effect="light">{{ statusText(d.order.status) }}</el-tag>
        <el-button style="margin-left:auto" @click="router.back()">返回</el-button>
        <el-button v-if="d.order.status === 'PENDING_DISPATCH'" type="primary" @click="evaluate">执行联合调度计算</el-button>
        <el-button v-if="d.order.status === 'RUNNING'" type="primary" @click="transit('finish')">完成各点清运</el-button>
        <el-button v-if="d.order.status === 'PENDING_CONFIRM'" type="success" @click="transit('confirm')">确认交接</el-button>
      </div>
      <div style="display:flex;gap:28px;margin-top:12px;font-size:13px;color:var(--text2);flex-wrap:wrap">
        <span>责任人 <b style="color:var(--text)">{{ d.driver?.name || '未派单' }}</b></span>
        <span>车辆 <b style="color:var(--text)">{{ d.vehicle?.plateNo || '-' }}</b></span>
        <span>计划时间 <b class="num" style="color:var(--text)">{{ formatTime(d.order.planTime) }}</b></span>
        <span>创建时间 <b class="num" style="color:var(--text)">{{ formatTime(d.order.createTime) }}</b></span>
        <span>最近更新 <b class="num" style="color:var(--text)">{{ formatTime(d.order.updateTime) }}</b></span>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <div>
        <div class="card"><div class="card-h"><h2>任务信息</h2></div><div class="card-b">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="收集点">{{ d.order.pointSummary }}</el-descriptions-item>
            <el-descriptions-item label="任务类型">{{ { PLAN: '周期计划', URGENT: '紧急插单', MERGE: '合并任务' }[d.order.orderType] }}</el-descriptions-item>
            <el-descriptions-item label="预估重量">{{ d.order.estimatedWeight }} 吨</el-descriptions-item>
            <el-descriptions-item label="实际重量">{{ d.order.actualWeight ?? '-' }} 吨</el-descriptions-item>
            <el-descriptions-item label="取消/异常原因">{{ d.order.reason || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div></div>

        <div class="card"><div class="card-h"><h2>执行明细</h2></div>
          <el-table :data="d.stops" border size="small">
            <el-table-column prop="seq" label="序" width="50" />
            <el-table-column prop="pointId" label="点位ID" width="80" />
            <el-table-column label="到场" min-width="80"><template #default="{ row }">{{ formatTime(row.arriveTime).slice(11) }}</template></el-table-column>
            <el-table-column label="离场" min-width="80"><template #default="{ row }">{{ formatTime(row.leaveTime).slice(11) }}</template></el-table-column>
            <el-table-column prop="actualWeight" label="实际重量" min-width="90" align="right" />
            <el-table-column label="现场" width="80">
              <template #default="{ row }"><img v-if="row.siteImage" class="thumb" :src="row.siteImage" alt="" /></template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }"><el-tag size="small" :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag></template>
            </el-table-column>
          </el-table>
        </div>

        <div class="card"><div class="card-h"><h2>流转记录</h2></div><div class="card-b">
          <el-timeline>
            <el-timeline-item v-for="f in d.flows" :key="f.id" :timestamp="formatTime(f.createTime)" placement="top">
              <b>{{ f.action }}</b> · {{ f.operator }}
              <div class="muted">{{ statusText(f.fromStatus) }} → {{ statusText(f.toStatus) }}</div>
              <div v-if="f.reason" class="muted">原因：{{ f.reason }}</div>
            </el-timeline-item>
          </el-timeline>
        </div></div>
      </div>

      <div>
        <div class="card">
          <div class="card-h"><h2>容量与时效联合调度 · 计算留痕</h2>
            <el-tag v-if="latest" type="success" style="margin-left:auto">规则 v{{ latest.ruleVersion }}</el-tag>
          </div>
          <div class="card-b" v-if="latest">
            <div style="display:flex;align-items:center;gap:20px;background:#F7F9FC;padding:16px;border-radius:6px">
              <div class="num" style="font-size:40px;font-weight:600" :style="{ color: latest.grade === 'P1' ? '#B3261E' : latest.grade === 'P2' ? '#B26B00' : '#2F6B8A' }">
                {{ latest.totalScore }}
              </div>
              <div style="font-size:13px;color:var(--text2);line-height:22px">
                <b>{{ latest.grade }}</b> · {{ GRADE[latest.grade] }}<br />
                计算时间 {{ formatTime(latest.createTime) }}
              </div>
            </div>
            <el-table :data="items" size="small" border style="margin-top:14px">
              <el-table-column prop="name" label="输入因素" />
              <el-table-column prop="raw" label="原始值" />
              <el-table-column prop="weight" label="权重" align="right" />
              <el-table-column prop="score" label="得分" align="right" />
            </el-table>
            <div class="hint" style="margin-top:14px">
              <b>主要影响因素</b>：{{ latest.factors }}<br />
              <b>未满足条件</b>：{{ latest.unmet }}<br />
              <b>可改进项</b>：{{ latest.improve }}
            </div>
            <el-button style="margin-top:12px" @click="adjust">人工调整</el-button>
          </div>
          <el-empty v-else description="尚未执行联合调度计算" />
        </div>

        <div class="card" v-if="d.weighing"><div class="card-h"><h2>处置交接</h2></div><div class="card-b">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="称重单号">{{ d.weighing.recordNo }}</el-descriptions-item>
            <el-descriptions-item label="进场重量">{{ d.weighing.inWeight }} 吨</el-descriptions-item>
            <el-descriptions-item label="出场重量">{{ d.weighing.outWeight }} 吨</el-descriptions-item>
            <el-descriptions-item label="净重">{{ d.weighing.netWeight }} 吨</el-descriptions-item>
            <el-descriptions-item label="偏差">{{ d.weighing.deviation }}%</el-descriptions-item>
            <el-descriptions-item label="复核状态">
              <el-tag :type="statusType(d.weighing.reviewStatus)">{{ statusText(d.weighing.reviewStatus) }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <img v-if="d.weighing.weighingImage" :src="d.weighing.weighingImage" style="width:100%;margin-top:12px;border-radius:6px" alt="" />
        </div></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const GRADE = { P1: '立即派车', P2: '建议派车', P3: '可延后', NONE: '不推荐' }
const route = useRoute()
const router = useRouter()
const d = ref({})

const latest = computed(() => (d.value.scores && d.value.scores.length ? d.value.scores[0] : null))
const items = computed(() => {
  const s = latest.value
  if (!s) return []
  return [
    { name: '满载度', raw: s.vLoad + '%', weight: '—', score: s.sLoad },
    { name: '滞留时长', raw: s.vStay + ' 小时', weight: '—', score: s.sStay },
    { name: '投诉次数', raw: s.vComplaint + ' 次', weight: '—', score: s.sComplaint },
    { name: '车辆剩余容量', raw: s.vCapacity + ' 吨', weight: '—', score: s.sCapacity },
    { name: '点位距离', raw: s.vDistance + ' km', weight: '—', score: s.sDistance },
    { name: '垃圾类型匹配', raw: s.vTypeMatch ? '完全匹配' : '不匹配', weight: '—', score: s.sTypeMatch }
  ]
})

async function load() {
  d.value = await request.get('/api/dispatch/' + route.params.id)
}
async function evaluate() {
  const s = await request.get('/api/rule/options')
  await request.post('/api/dispatch/' + route.params.id + '/evaluate')
  ElMessage.success('计算完成，已写入留痕')
  load()
}
async function transit(action) {
  await ElMessageBox.confirm('确认执行该流转操作？', '状态流转', { type: 'info' })
  await request.post('/api/dispatch/' + route.params.id + '/transition', { action })
  ElMessage.success('操作成功')
  load()
}
async function adjust() {
  const { value } = await ElMessageBox.prompt('请填写人工调整原因（不少于 5 个字），原始计算结果不会被覆盖', '人工调整', {
    inputPlaceholder: '例如：原定车辆年检到期，改派同载重车辆'
  })
  await request.post('/api/dispatch/' + route.params.id + '/adjust', { reason: value })
  ElMessage.success('已记录人工调整')
  load()
}
onMounted(load)
</script>
""")

add("views/RuleConfig.vue", r"""
<template>
  <div style="display:grid;grid-template-columns:1.3fr 1fr;gap:16px;align-items:start">
    <div class="card">
      <div class="card-h"><h2>权重配置</h2>
        <el-tag v-if="rule" type="success" style="margin-left:auto">规则 v{{ rule.version }} 启用中</el-tag>
      </div>
      <div class="card-b">
        <div class="hint" style="margin-bottom:16px">
          权重合计必须等于 100%，保存后生成新版本并记录生效时间；历史计算仍引用原版本，保证结果可追溯。
        </div>
        <el-form label-width="140px">
          <el-form-item v-for="f in FIELDS" :key="f.prop" :label="f.label">
            <el-input-number v-model="form[f.prop]" :min="0" :max="100" @change="checkSum" style="width:120px" />
            <span class="muted" style="margin-left:10px">{{ f.tip }}</span>
          </el-form-item>
          <el-form-item label="P1 阈值">≥ <el-input-number v-model="form.thresholdP1" :min="0" :max="100" style="width:100px" /> 分</el-form-item>
          <el-form-item label="P2 阈值">≥ <el-input-number v-model="form.thresholdP2" :min="0" :max="100" style="width:100px" /> 分</el-form-item>
          <el-form-item label="P3 阈值">≥ <el-input-number v-model="form.thresholdP3" :min="0" :max="100" style="width:100px" /> 分</el-form-item>
          <el-form-item label="净重复核阈值"><el-input-number v-model="form.reviewThreshold" :min="0" :max="50" style="width:100px" /> %</el-form-item>
          <el-form-item label="权重合计">
            <b class="num" :style="{ color: sum === 100 ? '#2E7D5B' : '#B3261E' }">{{ sum }}%</b>
            <span class="muted" style="margin-left:10px">{{ sum === 100 ? '校验通过' : '必须等于 100%' }}</span>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="sum !== 100" @click="save">保存并生效</el-button>
            <el-button @click="load">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div>
      <div class="card"><div class="card-h"><h2>版本记录</h2></div><div class="card-b">
        <el-timeline>
          <el-timeline-item v-for="v in versions" :key="v.id" :timestamp="formatTime(v.effectiveTime)" placement="top">
            <b>v{{ v.version }}</b> {{ v.enabled === 1 ? '（启用中）' : '' }}
            <div class="muted">操作人 {{ v.createBy }}</div>
          </el-timeline-item>
        </el-timeline>
      </div></div>
      <div class="card"><div class="card-h"><h2>效果统计</h2></div><div class="card-b">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="计算总次数">{{ effect.total ?? 0 }}</el-descriptions-item>
          <el-descriptions-item label="推荐采纳率">{{ effect.adoptRate ?? 0 }}%</el-descriptions-item>
          <el-descriptions-item label="人工调整率">{{ effect.manualRate ?? 0 }}%</el-descriptions-item>
        </el-descriptions>
      </div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const FIELDS = [
  { prop: 'wLoad', label: '满载度', tip: '点位当前满载率，越高越紧急' },
  { prop: 'wStay', label: '滞留时长', tip: '距上次清运小时数' },
  { prop: 'wComplaint', label: '投诉次数', tip: '近 30 天该点位投诉量' },
  { prop: 'wCapacity', label: '车辆剩余容量', tip: '可用载重与预估重量之差' },
  { prop: 'wDistance', label: '点位距离', tip: '预置坐标直线距离' },
  { prop: 'wTypeMatch', label: '垃圾类型匹配', tip: '车辆类型与垃圾类型一致性' }
]
const rule = ref(null)
const versions = ref([])
const effect = reactive({})
const form = reactive({ wLoad: 26, wStay: 24, wComplaint: 16, wCapacity: 18, wDistance: 10, wTypeMatch: 6,
  thresholdP1: 85, thresholdP2: 65, thresholdP3: 45, reviewThreshold: 5 })

const sum = computed(() => FIELDS.reduce((s, f) => s + (Number(form[f.prop]) || 0), 0))
function checkSum() { /* 合计由 computed 实时展示 */ }

async function load() {
  const list = await request.get('/api/rule/options')
  versions.value = (list || []).sort((a, b) => b.version - a.version)
  rule.value = versions.value.find((v) => v.enabled === 1) || versions.value[0]
  if (rule.value) {
    FIELDS.forEach((f) => { form[f.prop] = rule.value[f.prop] })
    form.thresholdP1 = rule.value.thresholdP1
    form.thresholdP2 = rule.value.thresholdP2
    form.thresholdP3 = rule.value.thresholdP3
    form.reviewThreshold = rule.value.reviewThreshold
  }
  Object.assign(effect, await request.get('/api/score/effect'))
}
async function save() {
  const next = { ...form, version: (rule.value?.version || 0) + 1, ruleName: '容量与时效联合调度规则', enabled: 1 }
  await request.post('/api/rule', next)
  // 停用其它版本，保证只有一个启用
  for (const v of versions.value) {
    if (v.enabled === 1) await request.put('/api/rule/' + v.id, { ...v, enabled: 0 })
  }
  ElMessage.success('已生成新版本 v' + next.version)
  load()
}
onMounted(load)
</script>
""")

add("views/Report.vue", r"""
<template>
  <div>
    <div class="card"><div class="card-b">
      <div class="filter-bar">
        <el-select v-model="range" style="width:180px">
          <el-option label="近 30 天" value="30" /><el-option label="本月" value="month" />
          <el-option label="本季度" value="quarter" /><el-option label="本年" value="year" />
        </el-select>
        <el-button type="primary" @click="load">刷新统计</el-button>
        <el-button @click="exportCsv">导出当前统计</el-button>
      </div>
    </div></div>
    <div class="card"><div class="card-h"><h2>关键指标</h2></div><div class="card-b">
      <el-descriptions :column="3" border>
        <el-descriptions-item label="清运量">{{ kpi.volume ?? 0 }} 吨</el-descriptions-item>
        <el-descriptions-item label="按时完成率">{{ kpi.onTimeRate ?? 0 }}%</el-descriptions-item>
        <el-descriptions-item label="满溢点位">{{ kpi.overflowPoints ?? 0 }} 处</el-descriptions-item>
        <el-descriptions-item label="车辆利用率">{{ kpi.vehicleUsage ?? 0 }}%</el-descriptions-item>
        <el-descriptions-item label="投诉量">{{ kpi.complaints ?? 0 }} 件</el-descriptions-item>
        <el-descriptions-item label="异常未闭环">{{ kpi.abnormalOpen ?? 0 }} 条</el-descriptions-item>
      </el-descriptions>
    </div></div>
    <div class="card"><div class="card-h"><h2>任务状态分布</h2></div>
      <el-table :data="statusDist" border>
        <el-table-column prop="name" label="状态" />
        <el-table-column prop="value" label="任务数" align="right" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const range = ref('30')
const kpi = reactive({})
const statusDist = ref([])

async function load() {
  const d = await request.get('/api/report/dashboard')
  Object.assign(kpi, d.kpi || {})
  statusDist.value = d.statusDist || []
}
function exportCsv() {
  const rows = [['指标', '数值'], ['清运量', kpi.volume], ['按时完成率', kpi.onTimeRate + '%'],
    ['满溢点位', kpi.overflowPoints], ['车辆利用率', kpi.vehicleUsage + '%'], ['投诉量', kpi.complaints]]
  const csv = rows.map((r) => r.join(',')).join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = '环卫运营统计.csv'
  a.click()
  ElMessage.success('已导出')
}
onMounted(load)
</script>
""")

add("views/Profile.vue", r"""
<template>
  <div style="display:grid;grid-template-columns:380px 1fr;gap:16px;align-items:start">
    <div class="card"><div class="card-b" style="text-align:center">
      <el-upload :show-file-list="false" :http-request="uploadAvatar">
        <img class="big-avatar" :src="form.avatar || '/uploads/seed/avatar/01.jpg'" alt="" />
      </el-upload>
      <div class="muted" style="margin-top:10px">点击头像更换（JPG/PNG ≤5MB）</div>
      <h3 style="margin:10px 0 2px">{{ store.user?.realName }}</h3>
      <div class="muted">{{ store.user?.roleName }}</div>
    </div></div>

    <div>
      <div class="card"><div class="card-h"><h2>基本资料</h2></div><div class="card-b">
        <el-form :model="form" label-width="100px">
          <el-form-item label="账号"><el-input v-model="form.username" disabled style="width:320px" /></el-form-item>
          <el-form-item label="姓名"><el-input v-model="form.realName" style="width:320px" /></el-form-item>
          <el-form-item label="手机号"><el-input v-model="form.phone" style="width:320px" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="form.email" style="width:320px" /></el-form-item>
          <el-form-item><el-button type="primary" @click="saveProfile">保存资料</el-button></el-form-item>
        </el-form>
      </div></div>

      <div class="card"><div class="card-h"><h2>修改密码</h2></div><div class="card-b">
        <el-form label-width="100px">
          <el-form-item label="原密码"><el-input v-model="pwd.oldPassword" type="password" style="width:320px" show-password /></el-form-item>
          <el-form-item label="新密码"><el-input v-model="pwd.newPassword" type="password" style="width:320px" show-password /></el-form-item>
          <el-form-item><el-button type="primary" @click="savePwd">修改密码</el-button></el-form-item>
        </el-form>
      </div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { store } from '@/store/user'

const form = reactive({ username: '', realName: '', phone: '', email: '', avatar: '' })
const pwd = reactive({ oldPassword: '', newPassword: '' })

async function load() {
  const d = await request.get('/api/auth/me')
  Object.assign(form, d.user)
  store.setLogin(d.user, d.menus)
}
async function uploadAvatar(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.avatar = d.path
  await request.put('/api/auth/profile', form)
  ElMessage.success('头像已更新')
  load()
}
async function saveProfile() {
  await request.put('/api/auth/profile', form)
  ElMessage.success('资料已保存')
  load()
}
async function savePwd() {
  if (!pwd.oldPassword || !pwd.newPassword) { ElMessage.warning('请填写完整'); return }
  await request.post('/api/auth/password', pwd)
  ElMessage.success('密码已修改')
  pwd.oldPassword = ''; pwd.newPassword = ''
}
onMounted(load)
</script>

<style scoped>
.big-avatar { width: 96px; height: 96px; border-radius: 50%; object-fit: cover; cursor: pointer; border: 2px solid #E3E8EF; }
</style>
""")

add("views/MyTasks.vue", r"""
<template>
  <div class="phone-wrap">
    <div class="phone">
      <div class="ph-top">
        <div class="ph-title">我的清运任务</div>
        <div class="ph-sub">{{ store.user?.realName }} · 司机端</div>
      </div>
      <div class="ph-body">
        <div class="stat">
          <div><b style="color:#B26B00">{{ counts.wait }}</b><span>待执行</span></div>
          <div><b style="color:#2F6B8A">{{ counts.run }}</b><span>进行中</span></div>
          <div><b style="color:#2E7D5B">{{ counts.done }}</b><span>已完成</span></div>
        </div>
        <div v-for="t in tasks" :key="t.id" class="task">
          <div class="r1">
            <el-tag size="small" :type="statusType(t.status)">{{ statusText(t.status) }}</el-tag>
            <span class="no">{{ t.orderNo }}</span>
          </div>
          <h4>{{ t.pointSummary }}</h4>
          <div class="m">计划 {{ formatTime(t.planTime) }} · 预估 {{ t.estimatedWeight }} 吨</div>
          <div class="foot">
            <el-button v-if="t.status === 'ACCEPTED'" size="small" @click="act(t, 'start')">开始执行</el-button>
            <el-button v-if="t.status === 'RUNNING'" size="small" type="primary" @click="act(t, 'finish')">完成清运</el-button>
            <el-button size="small" @click="router.push('/dispatch/' + t.id)">查看详情</el-button>
          </div>
        </div>
        <el-empty v-if="!tasks.length" description="当前没有分配给您的任务" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { store } from '@/store/user'
import { formatTime, statusText, statusType } from '@/utils/format'

const router = useRouter()
const tasks = ref([])
const counts = reactive({ wait: 0, run: 0, done: 0 })

async function load() {
  const d = await request.get('/api/dispatch/page', { params: { page: 1, size: 50 } })
  const all = d.list || []
  tasks.value = all.filter((t) => ['ACCEPTED', 'RUNNING', 'PENDING_CONFIRM'].includes(t.status))
  counts.wait = all.filter((t) => t.status === 'ACCEPTED').length
  counts.run = all.filter((t) => t.status === 'RUNNING').length
  counts.done = all.filter((t) => t.status === 'DONE').length
}
async function act(t, action) {
  if (action === 'finish') {
    await ElMessageBox.confirm('确认各站点清运已完成？提交后进入待确认状态。', '完成确认', { type: 'info' })
  }
  await request.post('/api/dispatch/' + t.id + '/transition', { action })
  ElMessage.success('操作成功')
  load()
}
onMounted(load)
</script>

<style scoped>
.phone-wrap { display: grid; place-items: center; padding: 8px 0; }
.phone { width: 390px; background: #F5F7FA; border-radius: 20px; border: 8px solid #1B2430;
  box-shadow: 0 18px 50px rgba(27,36,48,.24); overflow: hidden; }
.ph-top { background: #2F6B8A; color: #fff; padding: 16px 18px; }
.ph-title { font-size: 17px; font-weight: 600; }
.ph-sub { font-size: 12px; opacity: .82; margin-top: 4px; }
.ph-body { padding: 14px; max-height: 640px; overflow-y: auto; }
.stat { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; }
.stat div { background: #fff; border: 1px solid #E3E8EF; border-radius: 8px; padding: 10px; text-align: center; }
.stat b { display: block; font-size: 18px; }
.stat span { font-size: 11px; color: #5B6675; }
.task { background: #fff; border: 1px solid #E3E8EF; border-radius: 8px; padding: 14px; margin-bottom: 12px; }
.r1 { display: flex; align-items: center; gap: 8px; }
.no { font-size: 12px; color: #8A94A3; font-variant-numeric: tabular-nums; }
.task h4 { font-size: 15px; margin: 8px 0 4px; }
.m { font-size: 12px; color: #5B6675; }
.foot { display: flex; gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #EEF1F5; }
</style>
""")

for path, content in F.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
print("生成", len(F), "个页面")
