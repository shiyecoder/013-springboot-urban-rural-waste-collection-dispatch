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
