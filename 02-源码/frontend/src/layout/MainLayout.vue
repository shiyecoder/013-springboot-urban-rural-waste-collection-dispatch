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
