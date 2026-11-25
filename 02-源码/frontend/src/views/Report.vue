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
