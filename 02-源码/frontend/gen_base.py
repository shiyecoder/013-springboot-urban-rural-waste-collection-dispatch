#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 NEW-013 前端（Vue 3 + Vite + Element Plus + ECharts）。"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "frontend/src")
F = {}

def add(rel, content):
    F[os.path.join(SRC, rel)] = content

add("main.js", r"""
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './styles/global.css'

const app = createApp(App)
for (const [key, comp] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, comp)
}
app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.mount('#app')
""")

add("App.vue", r"""
<template>
  <router-view />
</template>
""")

add("styles/global.css", r"""
:root {
  --primary: #1F2937;
  --secondary: #2F6B8A;
  --accent: #3B627A;
  --bg: #F5F7FA;
  --success: #2E7D5B;
  --danger: #B3261E;
  --warning: #B26B00;
  --border: #E3E8EF;
  --text: #1B2430;
  --text2: #5B6675;
  --text3: #8A94A3;
  --el-color-primary: #1F2937;
  --el-color-success: #2E7D5B;
  --el-color-danger: #B3261E;
  --el-color-warning: #B26B00;
  --el-border-radius-base: 6px;
}
* { box-sizing: border-box; }
html, body, #app { height: 100%; margin: 0; }
body {
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 22px;
}
.num { font-variant-numeric: tabular-nums; }
.card {
  background: #fff; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 16px;
}
.card-h {
  height: 52px; display: flex; align-items: center; padding: 0 20px; gap: 12px;
  border-bottom: 1px solid var(--border);
}
.card-h h2 { font-size: 16px; font-weight: 600; margin: 0; }
.card-b { padding: 20px; }
.page-title { font-size: 20px; font-weight: 600; line-height: 28px; margin: 0 0 16px; }
.filter-bar { display: flex; flex-wrap: wrap; gap: 12px 16px; align-items: center; }
.filter-bar .el-select, .filter-bar .el-input { width: 200px; }
.filter-bar .el-date-editor { width: 200px; }
.tbl-cell-sub { display: block; font-size: 12px; color: var(--text3); }
.el-table th.el-table__cell { background: #F7F9FC; color: var(--text2); font-weight: 500; }
.el-table .cell { line-height: 22px; }
.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 12px; }
.kpi {
  background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px;
}
.kpi .k { font-size: 13px; color: var(--text2); }
.kpi .v { font-size: 24px; font-weight: 600; line-height: 32px; margin-top: 2px; }
.kpi .d { font-size: 12px; color: var(--text3); }
.up { color: var(--danger); }
.down { color: var(--success); }
.chart-grid {
  display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 12px;
}
.chart-box { background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 10px 14px 4px; }
.chart-box h3 { font-size: 14px; margin: 0 0 4px; font-weight: 600; }
.chart { height: 168px; width: 100%; }
.tag-p1 { color: #B3261E; background: #FBEDEC; }
.tag-p2 { color: #B26B00; background: #FDF6E7; }
.tag-p3 { color: #2F6B8A; background: #EAF2F6; }
.thumb { width: 64px; height: 48px; border-radius: 4px; object-fit: cover; border: 1px solid var(--border); }
.muted { color: var(--text3); font-size: 13px; }
.hint {
  background: #EAF2F6; border-left: 3px solid var(--secondary); padding: 10px 14px;
  border-radius: 4px; font-size: 13px; color: #254E66; line-height: 22px;
}
""")

add("utils/format.js", r"""
/**
 * 全局时间格式化：全系统统一调用，禁止各页面自行拼接
 * @param {string|Date} v 时间值
 * @param {boolean} dateOnly 是否只显示日期
 */
export function formatTime(v, dateOnly = false) {
  if (!v) return '-'
  const s = String(v).replace('T', ' ')
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ ]?(\d{2}):(\d{2}):(\d{2})/)
  if (m) {
    return dateOnly ? `${m[1]}-${m[2]}-${m[3]}` : `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}:${m[6]}`
  }
  return s
}

export function formatDate(v) {
  return formatTime(v, true)
}

/** 状态字典 → 中文标签与颜色 */
export const STATUS_TEXT = {
  PENDING_DISPATCH: '待派车',
  ACCEPTED: '已接单',
  RUNNING: '清运中',
  PENDING_CONFIRM: '待确认',
  DONE: '已完成',
  CANCELED: '已取消',
  ABNORMAL: '异常',
  NORMAL: '正常',
  OVERFLOW: '满溢',
  DISABLED: '停用',
  IDLE: '空闲',
  BUSY: '作业中',
  MAINTAIN: '保养中',
  PENDING: '待处理',
  DISPATCHED: '已派单',
  OPEN: '待处理',
  HANDLING: '处理中',
  CLOSED: '已闭环',
  PASS: '复核通过',
  REVIEW: '待复核',
  ON: '启用',
  OFF: '停用',
  DUE: '待保养',
  ING: '保养中',
  SKIPPED: '已跳过',
  WAITING: '待执行',
  ARRIVED: '已到场'
}

export function statusText(s) {
  return STATUS_TEXT[s] || s || '-'
}

export function statusType(s) {
  if (['DONE', 'CLOSED', 'PASS', 'NORMAL', 'IDLE', 'ON'].includes(s)) return 'success'
  if (['RUNNING', 'ACCEPTED', 'PENDING_CONFIRM', 'HANDLING', 'ARRIVED', 'DISPATCHED', 'BUSY'].includes(s)) return 'primary'
  if (['PENDING_DISPATCH', 'PENDING', 'WAITING', 'DUE', 'OVERFLOW', 'REVIEW'].includes(s)) return 'warning'
  if (['ABNORMAL', 'CANCELED', 'OPEN', 'DISABLED'].includes(s)) return 'danger'
  return 'info'
}
""")

add("utils/request.js", r"""
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({ baseURL: '', timeout: 30000 })

service.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('wd_token')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})

service.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && typeof body.code !== 'undefined') {
      if (body.code === 0) return body.data
      if (body.code === 401) {
        localStorage.removeItem('wd_token')
        router.push('/login')
        ElMessage.error(body.msg || '登录已过期，请重新登录')
        return Promise.reject(new Error(body.msg))
      }
      ElMessage.error(body.msg || '请求失败')
      return Promise.reject(new Error(body.msg || '请求失败'))
    }
    return body
  },
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('wd_token')
      router.push('/login')
    }
    ElMessage.error(err.message || '网络异常')
    return Promise.reject(err)
  }
)

export default service
""")

add("store/user.js", r"""
import { reactive } from 'vue'

/** 轻量全局状态：登录人、角色、动态菜单 */
export const store = reactive({
  user: JSON.parse(localStorage.getItem('wd_user') || 'null'),
  menus: JSON.parse(localStorage.getItem('wd_menus') || '[]'),
  setLogin(user, menus) {
    this.user = user
    this.menus = menus || []
    localStorage.setItem('wd_user', JSON.stringify(user || null))
    localStorage.setItem('wd_menus', JSON.stringify(menus || []))
  },
  logout() {
    this.user = null
    this.menus = []
    localStorage.removeItem('wd_token')
    localStorage.removeItem('wd_user')
    localStorage.removeItem('wd_menus')
  }
})
""")

add("router/index.js", r"""
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '环卫运营看板' } },
      { path: 'point', component: () => import('@/views/PointList.vue'), meta: { title: '收集点管理' } },
      { path: 'vehicle', component: () => import('@/views/VehicleList.vue'), meta: { title: '车辆档案' } },
      { path: 'driver', component: () => import('@/views/DriverList.vue'), meta: { title: '司机档案' } },
      { path: 'route', component: () => import('@/views/RouteList.vue'), meta: { title: '线路与处置场' } },
      { path: 'plan', component: () => import('@/views/PlanList.vue'), meta: { title: '周期计划' } },
      { path: 'dispatch', component: () => import('@/views/DispatchConsole.vue'), meta: { title: '清运调度台' } },
      { path: 'dispatch/:id', component: () => import('@/views/DispatchDetail.vue'), meta: { title: '清运任务详情' } },
      { path: 'overflow', component: () => import('@/views/OverflowList.vue'), meta: { title: '临时报满' } },
      { path: 'weighing', component: () => import('@/views/WeighingList.vue'), meta: { title: '称重交接' } },
      { path: 'exception', component: () => import('@/views/ExceptionList.vue'), meta: { title: '异常处理' } },
      { path: 'maintenance', component: () => import('@/views/MaintenanceList.vue'), meta: { title: '车辆保养' } },
      { path: 'rule', component: () => import('@/views/RuleConfig.vue'), meta: { title: '调度规则配置' } },
      { path: 'score', component: () => import('@/views/ScoreList.vue'), meta: { title: '计算留痕' } },
      { path: 'report', component: () => import('@/views/Report.vue'), meta: { title: '统计报表' } },
      { path: 'user', component: () => import('@/views/UserList.vue'), meta: { title: '用户管理' } },
      { path: 'role', component: () => import('@/views/RoleList.vue'), meta: { title: '角色管理' } },
      { path: 'menu', component: () => import('@/views/MenuList.vue'), meta: { title: '菜单管理' } },
      { path: 'profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } },
      { path: 'my-task', component: () => import('@/views/MyTasks.vue'), meta: { title: '我的任务' } }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  if (to.meta && to.meta.public) return true
  const token = localStorage.getItem('wd_token')
  if (!token) return '/login'
  return true
})

export default router
""")

for path, content in F.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
print("基础文件", len(F))
