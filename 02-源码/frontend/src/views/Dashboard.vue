<template>
  <div>
    <div class="kpi-grid">
      <div class="kpi"><div class="k">近 30 天清运量</div>
        <div class="v num">{{ kpi.volume ?? 0 }}<span class="unit">吨</span></div>
        <div class="d"><span class="up">↑ 6.4%</span> 环比上月</div></div>
      <div class="kpi"><div class="k">按时完成率</div>
        <div class="v num">{{ kpi.onTimeRate ?? 0 }}%</div>
        <div class="d"><span class="up">↑ 2.1pt</span> 环比上月</div></div>
      <div class="kpi"><div class="k">满溢点位</div>
        <div class="v num">{{ kpi.overflowPoints ?? 0 }}<span class="unit">处</span></div>
        <div class="d">待处理上报 {{ kpi.overflowPending ?? 0 }} 条</div></div>
      <div class="kpi"><div class="k">车辆利用率</div>
        <div class="v num">{{ kpi.vehicleUsage ?? 0 }}%</div>
        <div class="d">按作业中车辆计算</div></div>
      <div class="kpi"><div class="k">投诉量</div>
        <div class="v num">{{ kpi.complaints ?? 0 }}<span class="unit">件</span></div>
        <div class="d"><span class="down">↓ 5 件</span> 环比上月</div></div>
      <div class="kpi"><div class="k">异常未闭环</div>
        <div class="v num" style="color:#B3261E">{{ kpi.abnormalOpen ?? 0 }}<span class="unit">条</span></div>
        <div class="d">任务总数 {{ kpi.orderTotal ?? 0 }} 单</div></div>
    </div>

    <div class="chart-grid">
      <div class="chart-box" style="grid-row: span 1">
        <h3>清运量与任务趋势（近 14 天）</h3><div ref="c1" class="chart"></div>
      </div>
      <div class="chart-box"><h3>任务状态分布</h3><div ref="c2" class="chart"></div></div>
      <div class="chart-box"><h3>垃圾类型容量构成</h3><div ref="c3" class="chart"></div></div>
      <div class="chart-box"><h3>区域任务排行</h3><div ref="c4" class="chart"></div></div>
      <div class="chart-box"><h3>任务阶段对比</h3><div ref="c5" class="chart"></div></div>
      <div class="chart-box"><h3>调度推荐结果分布</h3><div ref="c6" class="chart"></div></div>
    </div>
    <div class="hint" style="margin-top:12px">
      推荐采纳率 {{ data.adoptRate ?? 0 }}% · 人工调整率 {{ data.manualRate ?? 0 }}%
      —— 用于验证「容量与时效联合调度」创新模块是否被真实使用。
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'

const kpi = reactive({})
const data = reactive({})
const charts = []
const refs = []
const c1 = ref(null), c2 = ref(null), c3 = ref(null), c4 = ref(null), c5 = ref(null), c6 = ref(null)
const COLORS = ['#1F2937', '#2F6B8A', '#3B627A', '#7E8B9B', '#2E7D5B', '#B26B00']

function mk(el, option) {
  if (!el) return
  const c = echarts.init(el)
  c.setOption(option)
  charts.push(c)
}

async function load() {
  const d = await request.get('/api/report/dashboard')
  Object.assign(kpi, d.kpi || {})
  Object.assign(data, d)
  await nextTick()
  const t = d.trend || { dates: [], volume: [], orders: [] }
  refs.push(c1.value, c2.value, c3.value, c4.value, c5.value, c6.value)

  mk(c1.value, {
    grid: { left: 36, right: 12, top: 24, bottom: 24 },
    tooltip: { trigger: 'axis' },
    legend: { right: 0, top: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    xAxis: { type: 'category', data: t.dates, axisLine: { lineStyle: { color: '#E3E8EF' } },
      axisLabel: { fontSize: 10, color: '#8A94A3' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EEF1F5' } },
      axisLabel: { fontSize: 10, color: '#8A94A3' } },
    series: [
      { name: '清运量(吨)', type: 'line', smooth: true, data: t.volume, symbolSize: 4,
        lineStyle: { width: 2, color: '#2F6B8A' }, itemStyle: { color: '#2F6B8A' } },
      { name: '任务单数', type: 'line', smooth: true, data: t.orders, symbolSize: 4,
        lineStyle: { width: 2, color: '#B26B00', type: 'dashed' }, itemStyle: { color: '#B26B00' } }
    ]
  })
  mk(c2.value, {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, itemWidth: 8, itemHeight: 8, textStyle: { fontSize: 10 } },
    color: COLORS,
    series: [{ type: 'pie', radius: ['46%', '68%'], center: ['50%', '42%'],
      data: d.statusDist || [], label: { show: false } }]
  })
  mk(c3.value, {
    grid: { left: 76, right: 16, top: 10, bottom: 10 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#EEF1F5' } },
      axisLabel: { fontSize: 10, color: '#8A94A3' } },
    yAxis: { type: 'category', data: (d.wasteType || []).map((x) => x.name),
      axisLabel: { fontSize: 11, color: '#5B6675' }, axisLine: { show: false } },
    series: [{ type: 'bar', data: (d.wasteType || []).map((x) => x.value), barWidth: 12,
      itemStyle: { color: '#2F6B8A', borderRadius: [0, 3, 3, 0] } }]
  })
  mk(c4.value, {
    grid: { left: 80, right: 24, top: 10, bottom: 10 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#EEF1F5' } },
      axisLabel: { fontSize: 10, color: '#8A94A3' } },
    yAxis: { type: 'category', data: (d.areaRank || []).map((x) => x.name),
      axisLabel: { fontSize: 11, color: '#5B6675' }, axisLine: { show: false } },
    series: [{ type: 'bar', data: (d.areaRank || []).map((x) => x.value), barWidth: 12,
      itemStyle: { color: '#3B627A', borderRadius: [0, 3, 3, 0] } }]
  })
  mk(c5.value, {
    grid: { left: 36, right: 12, top: 16, bottom: 24 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: (d.onTimeByStatus || []).map((x) => x.name),
      axisLabel: { fontSize: 11, color: '#8A94A3' }, axisLine: { lineStyle: { color: '#E3E8EF' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#EEF1F5' } },
      axisLabel: { fontSize: 10, color: '#8A94A3' } },
    series: [{ type: 'bar', data: (d.onTimeByStatus || []).map((x) => x.value), barWidth: 22,
      itemStyle: { color: '#2F6B8A', borderRadius: [3, 3, 0, 0] } }]
  })
  mk(c6.value, {
    grid: { left: 70, right: 24, top: 10, bottom: 10 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#EEF1F5' } },
      axisLabel: { fontSize: 10, color: '#8A94A3' } },
    yAxis: { type: 'category', data: (d.scoreDist || []).map((x) => x.name),
      axisLabel: { fontSize: 11, color: '#5B6675' }, axisLine: { show: false } },
    series: [{ type: 'bar', data: (d.scoreDist || []).map((x) => x.value), barWidth: 12,
      itemStyle: { color: '#2E7D5B', borderRadius: [0, 3, 3, 0] } }]
  })
}

function resize() { charts.forEach((c) => c.resize()) }
onMounted(() => { load(); window.addEventListener('resize', resize) })
onBeforeUnmount(() => { window.removeEventListener('resize', resize); charts.forEach((c) => c.dispose()) })
</script>

<style scoped>
.unit { font-size: 13px; font-weight: 400; color: #5B6675; margin-left: 2px; }
</style>
