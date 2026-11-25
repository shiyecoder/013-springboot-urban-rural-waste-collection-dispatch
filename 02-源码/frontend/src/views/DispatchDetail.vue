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
