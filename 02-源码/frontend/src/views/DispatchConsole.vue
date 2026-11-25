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
