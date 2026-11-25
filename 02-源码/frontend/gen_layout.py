#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 NEW-013 前端布局、登录、看板与通用 CRUD 视图。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "frontend/src")
F = {}
def add(rel, c): F[os.path.join(SRC, rel)] = c

add("layout/MainLayout.vue", r"""
<template>
  <div class="layout">
    <aside class="side" :class="{ fold }">
      <div class="brand">
        <el-icon><Van /></el-icon>
        <span v-show="!fold">环卫清运调度</span>
      </div>
      <el-menu :default-active="route.path" :collapse="fold" :collapse-transition="false"
               background-color="#1F2937" text-color="rgba(255,255,255,.78)"
               active-text-color="#fff" router class="menu">
        <template v-for="g in store.menus" :key="g.id">
          <div class="grp" v-show="!fold">{{ g.name }}</div>
          <el-menu-item v-for="m in (g.children && g.children.length ? g.children : [g])"
                        :key="m.id" :index="m.path || '/dashboard'">
            <el-icon><component :is="iconOf(m.icon)" /></el-icon>
            <template #title>{{ m.name }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </aside>

    <div class="main">
      <header class="top">
        <el-icon class="fold-btn" @click="fold = !fold"><Fold v-if="!fold" /><Expand v-else /></el-icon>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>{{ crumbTop }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="right">
          <span class="muted">{{ today }}</span>
          <el-badge :value="unread" :hidden="unread === 0">
            <el-icon class="bell" @click="openMsg"><Bell /></el-icon>
          </el-badge>
          <el-dropdown @command="onCommand">
            <span class="who">
              <img class="avatar" :src="avatarUrl" alt="" />
              <span><b>{{ store.user?.realName }}</b>{{ store.user?.roleName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="content"><router-view /></main>
    </div>

    <el-drawer v-model="msgVisible" title="站内消息" size="420px">
      <div v-for="m in messages" :key="m.id" class="msg" @click="goMsg(m)">
        <div class="msg-t">{{ m.title }}<span class="muted">{{ formatTime(m.createTime) }}</span></div>
        <div class="msg-c">{{ m.content }}</div>
      </div>
      <el-empty v-if="!messages.length" description="暂无消息" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { store } from '@/store/user'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const fold = ref(false)
const messages = ref([])
const unread = ref(0)
const msgVisible = ref(false)

const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
const crumbTop = computed(() => {
  const g = store.menus.find((x) => (x.children || []).some((c) => c.path === route.path))
  return g ? g.name : '运营总览'
})
const avatarUrl = computed(() => store.user?.avatar || '')

const ICONS = { dashboard: 'DataBoard', point: 'Location', truck: 'Van', driver: 'User',
  route: 'Guide', dispatch: 'Tickets', overflow: 'Warning', weigh: 'Odometer',
  alert: 'Bell', wrench: 'Tools', rule: 'SetUp', report: 'TrendCharts',
  user: 'UserFilled', role: 'Avatar', menu: 'Menu' }
function iconOf(name) { return ICONS[name] || 'Menu' }

async function loadMessages() {
  try {
    const d = await request.get('/api/message/page', { params: { page: 1, size: 20 } })
    messages.value = d.list || []
    unread.value = messages.value.filter((m) => m.readFlag === 0).length
  } catch (e) { /* 消息失败不影响主流程 */ }
}
function openMsg() { msgVisible.value = true }
function goMsg(m) {
  msgVisible.value = false
  if (m.bizType === 'DISPATCH' && m.bizNo) router.push('/dispatch')
}
function onCommand(c) {
  if (c === 'profile') router.push('/profile')
  else { store.logout(); router.push('/login') }
}
onMounted(loadMessages)
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; }
.side { width: 220px; background: #1F2937; display: flex; flex-direction: column; transition: width .2s; }
.side.fold { width: 64px; }
.brand {
  height: 56px; display: flex; align-items: center; gap: 10px; padding: 0 18px;
  color: #fff; font-weight: 600; font-size: 15px; border-bottom: 1px solid rgba(255,255,255,.09);
}
.menu { border: none; flex: 1; overflow-y: auto; }
.grp { padding: 14px 18px 6px; font-size: 11px; color: rgba(255,255,255,.42); letter-spacing: 1px; }
.main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.top {
  height: 56px; background: #fff; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 16px; padding: 0 24px;
}
.fold-btn { cursor: pointer; font-size: 18px; color: var(--text2); }
.right { margin-left: auto; display: flex; align-items: center; gap: 18px; }
.bell { font-size: 18px; color: var(--text2); cursor: pointer; }
.who { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 12px; color: var(--text3); }
.who b { display: block; font-size: 13px; color: var(--text); font-weight: 500; }
.avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border); }
.content { flex: 1; overflow-y: auto; padding: 20px 24px; }
.msg { padding: 12px 0; border-bottom: 1px solid var(--border); cursor: pointer; }
.msg-t { display: flex; justify-content: space-between; font-size: 14px; font-weight: 500; }
.msg-c { font-size: 13px; color: var(--text2); margin-top: 4px; }
</style>
""")

add("views/Login.vue", r"""
<template>
  <div class="login">
    <div class="art" :style="{ backgroundImage: bg }">
      <div class="mask"></div>
      <div class="brandline"><el-icon size="22"><Van /></el-icon>环卫清运调度中心</div>
      <div class="hero">
        <h1>城乡垃圾清运<br />调度与台账管理系统</h1>
        <p>收集点报量 · 周期计划 · 紧急插单 · 途中改派 · 称重交接 · 异常闭环，把每一条清运线路都留成可核查的台账。</p>
        <ul>
          <li><b>128</b>在管收集点</li>
          <li><b>36</b>清运车辆</li>
          <li><b>99.2%</b>按时完成率</li>
        </ul>
      </div>
    </div>
    <div class="panel">
      <el-form class="form" :model="form" @submit.prevent="submit">
        <h2>账号登录</h2>
        <div class="sub">请使用单位分配的账号登录，连续 5 次失败将锁定 10 分钟</div>
        <el-form-item label="账号"><el-input v-model="form.username" size="large" placeholder="请输入账号" /></el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" size="large" show-password
                    placeholder="请输入密码" @keyup.enter="submit" />
        </el-form-item>
        <div class="err" v-if="err">{{ err }}</div>
        <el-checkbox v-model="remember">记住账号</el-checkbox>
        <el-button class="btn" type="primary" size="large" :loading="loading" @click="submit">登 录</el-button>
        <div class="roles">
          <div class="t">演示账号（点击填充）</div>
          <a @click="fill('admin')">运营管理员 admin / admin123<span>全部数据</span></a>
          <a @click="fill('dispatcher01')">调度员 dispatcher01 / admin123<span>调度范围</span></a>
          <a @click="fill('point01')">收集点管理员 point01 / admin123<span>本点位</span></a>
          <a @click="fill('driver01')">司机 driver01 / admin123<span>本人任务</span></a>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { store } from '@/store/user'

const router = useRouter()
const loading = ref(false)
const err = ref('')
const remember = ref(true)
const savedName = localStorage.getItem('wd_last_user')
const form = reactive({ username: savedName || 'admin', password: savedName ? '' : 'admin123' })
// 主题背景图：本地静态资源，断网也能显示
const bg = computed(() => "url('/uploads/seed/login/01.jpg')")

function fill(u) { form.username = u; form.password = 'admin123'; err.value = '' }

async function submit() {
  if (!form.username || !form.password) { err.value = '请输入账号与密码'; return }
  loading.value = true
  err.value = ''
  try {
    const d = await request.post('/api/auth/login', form)
    localStorage.setItem('wd_token', d.token)
    store.setLogin(d.user, d.menus)
    if (remember.value) localStorage.setItem('wd_last_user', form.username)
    ElMessage.success('登录成功')
    router.push(d.user && d.user.roleCode === 'DRIVER' ? '/my-task' : '/dashboard')
  } catch (e) {
    err.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login { display: grid; grid-template-columns: 1.15fr .85fr; height: 100vh; background: #EEF1F5; }
.art { position: relative; background-size: cover; background-position: center; color: #fff;
  display: flex; flex-direction: column; padding: 48px 56px; }
.mask { position: absolute; inset: 0;
  background: linear-gradient(150deg, rgba(31,41,55,.94) 0%, rgba(36,54,69,.88) 45%, rgba(47,107,138,.72) 100%); }
.brandline { position: relative; display: flex; align-items: center; gap: 10px; font-weight: 600; letter-spacing: .5px; }
.hero { position: relative; margin-top: auto; }
.hero h1 { font-size: 30px; line-height: 44px; font-weight: 600; letter-spacing: .5px; }
.hero p { color: rgba(255,255,255,.72); max-width: 440px; line-height: 24px; margin-top: 14px; }
.hero ul { list-style: none; display: flex; gap: 36px; padding: 0; margin-top: 32px; }
.hero li { font-size: 13px; color: rgba(255,255,255,.8); }
.hero li b { display: block; font-size: 24px; color: #fff; }
.panel { display: grid; place-items: center; background: #fff; padding: 40px; }
.form { width: 360px; }
.form h2 { font-size: 22px; margin: 0; }
.sub { color: var(--text3); font-size: 13px; margin: 6px 0 24px; }
.btn { width: 100%; height: 44px; margin-top: 16px; }
.err { color: var(--danger); font-size: 12px; margin: -6px 0 10px; }
.roles { margin-top: 24px; border-top: 1px solid var(--border); padding-top: 14px; }
.roles .t { font-size: 12px; color: var(--text3); margin-bottom: 6px; }
.roles a { display: flex; justify-content: space-between; padding: 6px 8px; border-radius: 6px;
  font-size: 13px; color: var(--text2); cursor: pointer; }
.roles a:hover { background: #F5F7FA; color: #1F2937; }
</style>
""")

add("views/Dashboard.vue", r"""
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
    grid: { left: 60, right: 16, top: 10, bottom: 10 },
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
""")

for path, content in F.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
print("生成", len(F), "个视图")
