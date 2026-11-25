<template>
  <div>
    <div class="card"><div class="card-b">
      <div class="filter-bar">
        <el-input v-model="q.kw" placeholder="点位编码 / 名称" clearable @keyup.enter="reload" />
        <el-select v-model="q.area" placeholder="所属区域" clearable>
          <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
        </el-select>
        <el-select v-model="q.wasteType" placeholder="垃圾类型" clearable>
          <el-option v-for="w in WASTE" :key="w" :label="w" :value="w" />
        </el-select>
        <el-select v-model="q.status" placeholder="点位状态" clearable>
          <el-option label="正常" value="NORMAL" /><el-option label="满溢" value="OVERFLOW" />
          <el-option label="停用" value="DISABLED" />
        </el-select>
        <el-button type="primary" @click="reload">查询</el-button>
        <el-button @click="reset">重置</el-button>
        <el-button type="primary" plain style="margin-left:auto" @click="openAdd">
          <el-icon><Plus /></el-icon>新建收集点
        </el-button>
      </div>
    </div></div>

    <div class="card">
      <div class="card-h"><h2>收集点列表</h2>
        <div style="margin-left:auto" class="muted">共 {{ total }} 条</div>
      </div>
      <el-table :data="rows" v-loading="loading" border>
        <el-table-column label="现场" width="96">
          <template #default="{ row }"><img class="thumb" :src="row.coverImage" alt="" /></template>
        </el-table-column>
        <el-table-column prop="pointCode" label="点位编码" min-width="130" />
        <el-table-column label="点位名称" min-width="200">
          <template #default="{ row }">
            {{ row.pointName }}
            <span class="tbl-cell-sub">负责人 {{ row.manager }} · {{ row.managerPhone }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="area" label="所属区域" min-width="110" />
        <el-table-column prop="wasteType" label="垃圾类型" min-width="110" />
        <el-table-column prop="capacity" label="容量(吨)" min-width="100" align="right" />
        <el-table-column label="满载度" min-width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.loadRate" :stroke-width="8"
                         :color="row.loadRate >= 85 ? '#B3261E' : row.loadRate >= 60 ? '#B26B00' : '#2E7D5B'" />
          </template>
        </el-table-column>
        <el-table-column label="最后清运" min-width="170">
          <template #default="{ row }"><span class="num">{{ formatTime(row.lastClearTime) }}</span></template>
        </el-table-column>
        <el-table-column label="状态" min-width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，可清空筛选或新建收集点" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:14px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10, 20, 50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-dialog v-model="visible" :title="form.id ? '编辑收集点' : '新建收集点'" width="680px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="点位编码" required>
          <el-input v-model="form.pointCode" :disabled="!!form.id" style="width:260px" />
        </el-form-item>
        <el-form-item label="点位名称" required><el-input v-model="form.pointName" style="width:360px" /></el-form-item>
        <el-form-item label="所属区域" required>
          <el-select v-model="form.area" style="width:200px">
            <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
          </el-select>
        </el-form-item>
        <el-form-item label="垃圾类型" required>
          <el-select v-model="form.wasteType" style="width:200px">
            <el-option v-for="w in WASTE" :key="w" :label="w" :value="w" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量(吨)" required>
          <el-input-number v-model="form.capacity" :precision="2" style="width:200px" />
        </el-form-item>
        <el-form-item label="当前装载量">
          <el-input-number v-model="form.currentLoad" :precision="2" style="width:200px" />
          <span class="muted" style="margin-left:8px">满载度由后端计算</span>
        </el-form-item>
        <el-form-item label="负责人"><el-input v-model="form.manager" style="width:200px" /></el-form-item>
        <el-form-item label="联系电话"><el-input v-model="form.managerPhone" style="width:200px" /></el-form-item>
        <el-form-item label="点位状态">
          <el-select v-model="form.status" style="width:200px">
            <el-option label="正常" value="NORMAL" /><el-option label="满溢" value="OVERFLOW" />
            <el-option label="停用" value="DISABLED" />
          </el-select>
        </el-form-item>
        <el-form-item label="现场图片">
          <el-upload :show-file-list="false" :http-request="upload">
            <img v-if="form.coverImage" class="thumb" style="width:120px;height:90px" :src="form.coverImage" alt="" />
            <el-button v-else size="small">上传图片</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusText, statusType } from '@/utils/format'

const WASTE = ['生活垃圾', '建筑垃圾', '餐厨垃圾', '大件垃圾', '园林绿化']
const q = reactive({ kw: '', area: '', wasteType: '', status: '' })
const rows = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const visible = ref(false)
const areas = ref([])
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/point/page', { params: { page: page.value, size: size.value, ...q } })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function reset() { Object.assign(q, { kw: '', area: '', wasteType: '', status: '' }); reload() }
function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, { status: 'NORMAL', capacity: 5, currentLoad: 0 })
  visible.value = true
}
function openEdit(row) { Object.keys(form).forEach((k) => delete form[k]); Object.assign(form, row); visible.value = true }
async function save() {
  if (form.id) await request.put('/api/point/' + form.id, form)
  else await request.post('/api/point', form)
  ElMessage.success('保存成功'); visible.value = false; load()
}
async function remove(row) {
  await ElMessageBox.confirm('该点位删除后不可恢复，确认删除？', '删除确认', { type: 'warning' })
  await request.delete('/api/point/' + row.id)
  ElMessage.success('已删除'); load()
}
async function upload(opt) {
  const fd = new FormData(); fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.coverImage = d.path
}
onMounted(async () => { areas.value = await request.get('/api/point/areas'); load() })
</script>
