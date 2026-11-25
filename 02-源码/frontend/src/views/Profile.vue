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
