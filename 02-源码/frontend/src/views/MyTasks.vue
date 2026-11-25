<template>
  <div class="phone-wrap">
    <div class="phone">
      <div class="ph-top">
        <div class="ph-title">我的清运任务</div>
        <div class="ph-sub">{{ store.user?.realName }} · 司机端</div>
      </div>
      <div class="ph-body">
        <div class="stat">
          <div><b style="color:#B26B00">{{ counts.wait }}</b><span>待执行</span></div>
          <div><b style="color:#2F6B8A">{{ counts.run }}</b><span>进行中</span></div>
          <div><b style="color:#2E7D5B">{{ counts.done }}</b><span>已完成</span></div>
        </div>
        <div v-for="t in tasks" :key="t.id" class="task">
          <div class="r1">
            <el-tag size="small" :type="statusType(t.status)">{{ statusText(t.status) }}</el-tag>
            <span class="no">{{ t.orderNo }}</span>
          </div>
          <h4>{{ t.pointSummary }}</h4>
          <div class="m">计划 {{ formatTime(t.planTime) }} · 预估 {{ t.estimatedWeight }} 吨</div>
          <div class="foot">
            <el-button v-if="t.status === 'ACCEPTED'" size="small" @click="act(t, 'start')">开始执行</el-button>
            <el-button v-if="t.status === 'RUNNING'" size="small" type="primary" @click="act(t, 'finish')">完成清运</el-button>
            <el-button size="small" @click="router.push('/dispatch/' + t.id)">查看详情</el-button>
          </div>
        </div>
        <el-empty v-if="!tasks.length" description="当前没有分配给您的任务" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { store } from '@/store/user'
import { formatTime, statusText, statusType } from '@/utils/format'

const router = useRouter()
const tasks = ref([])
const counts = reactive({ wait: 0, run: 0, done: 0 })

async function load() {
  const d = await request.get('/api/dispatch/page', { params: { page: 1, size: 50 } })
  const all = d.list || []
  tasks.value = all.filter((t) => ['ACCEPTED', 'RUNNING', 'PENDING_CONFIRM'].includes(t.status))
  counts.wait = all.filter((t) => t.status === 'ACCEPTED').length
  counts.run = all.filter((t) => t.status === 'RUNNING').length
  counts.done = all.filter((t) => t.status === 'DONE').length
}
async function act(t, action) {
  if (action === 'finish') {
    await ElMessageBox.confirm('确认各站点清运已完成？提交后进入待确认状态。', '完成确认', { type: 'info' })
  }
  await request.post('/api/dispatch/' + t.id + '/transition', { action })
  ElMessage.success('操作成功')
  load()
}
onMounted(load)
</script>

<style scoped>
.phone-wrap { display: grid; place-items: center; padding: 8px 0; }
.phone { width: 390px; background: #F5F7FA; border-radius: 20px; border: 8px solid #1B2430;
  box-shadow: 0 18px 50px rgba(27,36,48,.24); overflow: hidden; }
.ph-top { background: #2F6B8A; color: #fff; padding: 16px 18px; }
.ph-title { font-size: 17px; font-weight: 600; }
.ph-sub { font-size: 12px; opacity: .82; margin-top: 4px; }
.ph-body { padding: 14px; max-height: 640px; overflow-y: auto; }
.stat { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; }
.stat div { background: #fff; border: 1px solid #E3E8EF; border-radius: 8px; padding: 10px; text-align: center; }
.stat b { display: block; font-size: 18px; }
.stat span { font-size: 11px; color: #5B6675; }
.task { background: #fff; border: 1px solid #E3E8EF; border-radius: 8px; padding: 14px; margin-bottom: 12px; }
.r1 { display: flex; align-items: center; gap: 8px; }
.no { font-size: 12px; color: #8A94A3; font-variant-numeric: tabular-nums; }
.task h4 { font-size: 15px; margin: 8px 0 4px; }
.m { font-size: 12px; color: #5B6675; }
.foot { display: flex; gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #EEF1F5; }
</style>
