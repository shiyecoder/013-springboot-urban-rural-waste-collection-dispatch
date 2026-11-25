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
