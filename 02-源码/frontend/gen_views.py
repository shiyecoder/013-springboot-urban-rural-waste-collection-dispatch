#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 NEW-013 前端业务视图（通用 CRUD + 调度 / 规则 / 任务端 / 个人中心）。"""
import os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "frontend/src")
F = {}
def add(rel, c): F[os.path.join(SRC, rel)] = c

# ---------------- 通用 CRUD 组件 ----------------
add("components/CrudPage.vue", r"""
<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="kw" :placeholder="'搜索' + cfg.title" clearable @keyup.enter="reload" />
          <el-select v-if="cfg.statusOptions" v-model="status" placeholder="全部状态" clearable>
            <el-option v-for="o in cfg.statusOptions" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button v-if="!cfg.readonly" type="primary" plain style="margin-left:auto" @click="openAdd">
            <el-icon><Plus /></el-icon>新建
          </el-button>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-h">
        <h2>{{ cfg.title }}</h2>
        <div style="margin-left:auto" class="muted">共 {{ total }} 条</div>
      </div>
      <el-table :data="rows" v-loading="loading" border style="width:100%">
        <el-table-column v-for="c in cfg.columns" :key="c.prop" :prop="c.prop" :label="c.label"
                         :min-width="c.minWidth || 110" :align="c.align || 'left'" show-overflow-tooltip>
          <template #default="{ row }">
            <img v-if="c.type === 'image'" class="thumb" :src="row[c.prop]" alt="" />
            <el-tag v-else-if="c.type === 'status'" :type="statusType(row[c.prop])" effect="light">
              {{ statusText(row[c.prop]) }}
            </el-tag>
            <span v-else-if="c.type === 'time'" class="num">{{ formatTime(row[c.prop]) }}</span>
            <span v-else-if="c.type === 'date'" class="num">{{ formatDate(row[c.prop]) }}</span>
            <span v-else-if="c.type === 'num'" class="num">{{ row[c.prop] ?? '-' }}</span>
            <span v-else>{{ row[c.prop] ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="!cfg.readonly" label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下无记录，可清空筛选或新建" /></template>
      </el-table>
      <div style="display:flex;justify-content:flex-end;padding:14px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size"
                       :page-sizes="[10, 20, 50]" @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-dialog v-model="visible" :title="(form.id ? '编辑' : '新建') + cfg.title" width="640px">
      <el-form :model="form" label-width="110px">
        <el-form-item v-for="f in cfg.fields" :key="f.prop" :label="f.label" :required="f.required">
          <el-select v-if="f.type === 'select'" v-model="form[f.prop]" style="width:220px">
            <el-option v-for="o in f.options" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
          <el-input v-else-if="f.type === 'textarea'" v-model="form[f.prop]" type="textarea" :rows="3" />
          <el-date-picker v-else-if="f.type === 'date'" v-model="form[f.prop]" type="date"
                          value-format="YYYY-MM-DD" style="width:200px" />
          <el-input-number v-else-if="f.type === 'number'" v-model="form[f.prop]" :precision="f.precision || 0"
                           style="width:200px" />
          <el-upload v-else-if="f.type === 'image'" :show-file-list="false" :http-request="(o) => doUpload(o, f.prop)">
            <img v-if="form[f.prop]" class="thumb" style="width:96px;height:72px" :src="form[f.prop]" alt="" />
            <el-button v-else size="small">上传图片</el-button>
          </el-upload>
          <el-input v-else v-model="form[f.prop]" style="width:320px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, formatDate, statusText, statusType } from '@/utils/format'

const props = defineProps({ cfg: { type: Object, required: true } })
const cfg = props.cfg
const rows = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const kw = ref('')
const status = ref('')
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const form = reactive({})

async function load() {
  loading.value = true
  try {
    const d = await request.get(cfg.url + '/page', {
      params: { page: page.value, size: size.value, kw: kw.value, status: status.value }
    })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally { loading.value = false }
}
function reload() { page.value = 1; load() }
function reset() { kw.value = ''; status.value = ''; reload() }

function openAdd() {
  Object.keys(form).forEach((k) => delete form[k])
  cfg.fields.forEach((f) => { form[f.prop] = f.default ?? null })
  visible.value = true
}
function openEdit(row) {
  Object.keys(form).forEach((k) => delete form[k])
  Object.assign(form, JSON.parse(JSON.stringify(row)))
  visible.value = true
}
async function save() {
  saving.value = true
  try {
    if (form.id) await request.put(cfg.url + '/' + form.id, form)
    else await request.post(cfg.url, form)
    ElMessage.success('保存成功')
    visible.value = false
    load()
  } finally { saving.value = false }
}
async function remove(row) {
  await ElMessageBox.confirm('删除后不可恢复，确认删除该记录？', '删除确认', { type: 'warning' })
  await request.delete(cfg.url + '/' + row.id)
  ElMessage.success('已删除')
  load()
}
async function doUpload(opt, prop) {
  const fd = new FormData()
  fd.append('file', opt.file)
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form[prop] = d.path
  ElMessage.success('上传成功')
}
onMounted(load)
defineExpose({ reload })
</script>
""")

# ---------------- 通用视图工厂 ----------------
def simple(name, cfg_json, extra_import=""):
    add(f"views/{name}.vue", r"""
<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = __CFG__
</script>
""".replace("__CFG__", cfg_json))

simple("VehicleList", """{
  title: '车辆档案', url: '/api/vehicle',
  statusOptions: [
    { label: '空闲', value: 'IDLE' }, { label: '作业中', value: 'BUSY' },
    { label: '保养中', value: 'MAINTAIN' }, { label: '停用', value: 'DISABLED' }
  ],
  columns: [
    { prop: 'image', label: '车辆照片', type: 'image', minWidth: 100 },
    { prop: 'plateNo', label: '车牌号' },
    { prop: 'vehicleType', label: '车型' },
    { prop: 'loadCapacity', label: '载重(吨)', type: 'num', align: 'right' },
    { prop: 'mileage', label: '累计里程(km)', type: 'num', align: 'right' },
    { prop: 'annualCheckDate', label: '年检日期', type: 'date' },
    { prop: 'status', label: '状态', type: 'status' },
    { prop: 'remark', label: '备注', minWidth: 160 }
  ],
  fields: [
    { prop: 'plateNo', label: '车牌号', required: true },
    { prop: 'vehicleType', label: '车型', type: 'select', required: true, options: [
      { label: '压缩式', value: '压缩式' }, { label: '后装式', value: '后装式' },
      { label: '密闭罐式', value: '密闭罐式' }, { label: '勾臂式', value: '勾臂式' }] },
    { prop: 'loadCapacity', label: '载重(吨)', type: 'number', precision: 1, required: true },
    { prop: 'wasteTypes', label: '可收运类型' },
    { prop: 'annualCheckDate', label: '年检日期', type: 'date' },
    { prop: 'mileage', label: '累计里程', type: 'number' },
    { prop: 'status', label: '状态', type: 'select', default: 'IDLE', options: [
      { label: '空闲', value: 'IDLE' }, { label: '作业中', value: 'BUSY' },
      { label: '保养中', value: 'MAINTAIN' }, { label: '停用', value: 'DISABLED' }] },
    { prop: 'image', label: '车辆照片', type: 'image' },
    { prop: 'remark', label: '备注', type: 'textarea' }
  ]
}""")

simple("DriverList", """{
  title: '司机档案', url: '/api/driver',
  statusOptions: [{ label: '在岗', value: '1' }, { label: '离岗', value: '0' }],
  columns: [
    { prop: 'avatar', label: '头像', type: 'image', minWidth: 90 },
    { prop: 'driverNo', label: '司机编号' },
    { prop: 'name', label: '姓名' },
    { prop: 'phone', label: '联系电话' },
    { prop: 'licenseType', label: '准驾车型' },
    { prop: 'licenseExpire', label: '驾驶证有效期', type: 'date' },
    { prop: 'status', label: '状态', type: 'status' }
  ],
  fields: [
    { prop: 'driverNo', label: '司机编号', required: true },
    { prop: 'name', label: '姓名', required: true },
    { prop: 'phone', label: '联系电话', required: true },
    { prop: 'licenseNo', label: '驾驶证号', required: true },
    { prop: 'licenseType', label: '准驾车型', type: 'select', required: true, options: [
      { label: 'A2', value: 'A2' }, { label: 'B2', value: 'B2' }, { label: 'C1', value: 'C1' }] },
    { prop: 'licenseExpire', label: '驾驶证有效期', type: 'date', required: true },
    { prop: 'status', label: '状态', type: 'select', default: '1', options: [
      { label: '在岗', value: 1 }, { label: '离岗', value: 0 }] },
    { prop: 'avatar', label: '头像', type: 'image' }
  ]
}""")

simple("RouteList", """{
  title: '清运线路', url: '/api/route',
  columns: [
    { prop: 'routeCode', label: '线路编码' },
    { prop: 'routeName', label: '线路名称' },
    { prop: 'area', label: '所属区域' },
    { prop: 'distanceKm', label: '里程(km)', type: 'num', align: 'right' },
    { prop: 'stopCount', label: '站点数', type: 'num', align: 'right' },
    { prop: 'status', label: '状态', type: 'status' },
    { prop: 'remark', label: '备注', minWidth: 180 }
  ],
  fields: [
    { prop: 'routeCode', label: '线路编码', required: true },
    { prop: 'routeName', label: '线路名称', required: true },
    { prop: 'area', label: '所属区域', required: true },
    { prop: 'distanceKm', label: '里程(km)', type: 'number', precision: 1 },
    { prop: 'stopCount', label: '站点数', type: 'number' },
    { prop: 'status', label: '状态', type: 'select', default: 1, options: [
      { label: '启用', value: 1 }, { label: '停用', value: 0 }] },
    { prop: 'remark', label: '备注', type: 'textarea' }
  ]
}""")

simple("PlanList", """{
  title: '周期清运计划', url: '/api/plan',
  statusOptions: [{ label: '启用', value: 'ON' }, { label: '停用', value: 'OFF' }],
  columns: [
    { prop: 'planCode', label: '计划编码' },
    { prop: 'pointId', label: '收集点ID', type: 'num' },
    { prop: 'wasteType', label: '垃圾类型' },
    { prop: 'frequency', label: '频率' },
    { prop: 'estimatedWeight', label: '预估重量(吨)', type: 'num', align: 'right' },
    { prop: 'nextDate', label: '下次清运', type: 'date' },
    { prop: 'status', label: '状态', type: 'status' }
  ],
  fields: [
    { prop: 'planCode', label: '计划编码', required: true },
    { prop: 'pointId', label: '收集点ID', type: 'number', required: true },
    { prop: 'routeId', label: '默认线路ID', type: 'number' },
    { prop: 'wasteType', label: '垃圾类型', type: 'select', required: true, options: [
      { label: '生活垃圾', value: '生活垃圾' }, { label: '建筑垃圾', value: '建筑垃圾' },
      { label: '餐厨垃圾', value: '餐厨垃圾' }, { label: '大件垃圾', value: '大件垃圾' },
      { label: '园林绿化', value: '园林绿化' }] },
    { prop: 'frequency', label: '频率', type: 'select', default: 'DAILY', options: [
      { label: '每日', value: 'DAILY' }, { label: '隔日', value: 'EVERY_2_DAYS' },
      { label: '每周', value: 'WEEKLY' }] },
    { prop: 'estimatedWeight', label: '预估重量(吨)', type: 'number', precision: 1, required: true },
    { prop: 'nextDate', label: '下次清运', type: 'date', required: true },
    { prop: 'status', label: '状态', type: 'select', default: 'ON', options: [
      { label: '启用', value: 'ON' }, { label: '停用', value: 'OFF' }] }
  ]
}""")

simple("WeighingList", """{
  title: '称重交接', url: '/api/weighing',
  statusOptions: [{ label: '复核通过', value: 'PASS' }, { label: '待复核', value: 'REVIEW' }],
  readonly: false,
  columns: [
    { prop: 'recordNo', label: '称重单号' },
    { prop: 'orderId', label: '任务ID', type: 'num' },
    { prop: 'inWeight', label: '进场重量', type: 'num', align: 'right' },
    { prop: 'outWeight', label: '出场重量', type: 'num', align: 'right' },
    { prop: 'netWeight', label: '净重(吨)', type: 'num', align: 'right' },
    { prop: 'disposeType', label: '处置方式' },
    { prop: 'deviation', label: '偏差(%)', type: 'num', align: 'right' },
    { prop: 'reviewStatus', label: '复核状态', type: 'status' },
    { prop: 'weighingImage', label: '称重单', type: 'image', minWidth: 100 },
    { prop: 'weighTime', label: '称重时间', type: 'time' }
  ],
  fields: [
    { prop: 'orderId', label: '任务ID', type: 'number', required: true },
    { prop: 'disposeSiteId', label: '处置场ID', type: 'number', required: true },
    { prop: 'inWeight', label: '进场重量', type: 'number', precision: 2, required: true },
    { prop: 'outWeight', label: '出场重量', type: 'number', precision: 2, required: true },
    { prop: 'netWeight', label: '净重', type: 'number', precision: 2, required: true },
    { prop: 'disposeType', label: '处置方式', type: 'select', options: [
      { label: '填埋', value: 'LAND_FILL' }, { label: '焚烧发电', value: 'INCINERATE' },
      { label: '资源化利用', value: 'RECYCLE' }] },
    { prop: 'weighingImage', label: '称重单', type: 'image' }
  ]
}""")

simple("ExceptionList", """{
  title: '异常处理', url: '/api/exception',
  statusOptions: [{ label: '待处理', value: 'OPEN' }, { label: '处理中', value: 'HANDLING' },
    { label: '已闭环', value: 'CLOSED' }],
  columns: [
    { prop: 'exceptionNo', label: '异常编号' },
    { prop: 'orderId', label: '任务ID', type: 'num' },
    { prop: 'type', label: '异常类型' },
    { prop: 'description', label: '描述', minWidth: 200 },
    { prop: 'image', label: '现场图片', type: 'image', minWidth: 100 },
    { prop: 'reporter', label: '上报人' },
    { prop: 'handleResult', label: '处理结论', minWidth: 180 },
    { prop: 'status', label: '状态', type: 'status' },
    { prop: 'createTime', label: '上报时间', type: 'time' }
  ],
  fields: [
    { prop: 'orderId', label: '任务ID', type: 'number' },
    { prop: 'type', label: '异常类型', type: 'select', required: true, options: [
      { label: '车辆故障', value: 'VEHICLE_FAULT' }, { label: '收集点无法进入', value: 'UNREACHABLE' },
      { label: '重量超载', value: 'OVERLOAD' }, { label: '漏站', value: 'MISS_STOP' },
      { label: '其他', value: 'OTHER' }] },
    { prop: 'description', label: '描述', type: 'textarea', required: true },
    { prop: 'handleResult', label: '处理结论', type: 'textarea' },
    { prop: 'status', label: '状态', type: 'select', default: 'OPEN', options: [
      { label: '待处理', value: 'OPEN' }, { label: '处理中', value: 'HANDLING' },
      { label: '已闭环', value: 'CLOSED' }] },
    { prop: 'image', label: '现场图片', type: 'image' }
  ]
}""")

simple("MaintenanceList", """{
  title: '车辆保养', url: '/api/maintenance',
  statusOptions: [{ label: '已完成', value: 'DONE' }, { label: '待保养', value: 'DUE' },
    { label: '保养中', value: 'ING' }],
  columns: [
    { prop: 'vehicleId', label: '车辆ID', type: 'num' },
    { prop: 'maintainType', label: '保养类型' },
    { prop: 'maintainDate', label: '保养日期', type: 'date' },
    { prop: 'mileage', label: '保养里程', type: 'num', align: 'right' },
    { prop: 'nextDate', label: '下次日期', type: 'date' },
    { prop: 'cost', label: '费用(元)', type: 'num', align: 'right' },
    { prop: 'status', label: '状态', type: 'status' },
    { prop: 'remark', label: '说明', minWidth: 180 }
  ],
  fields: [
    { prop: 'vehicleId', label: '车辆ID', type: 'number', required: true },
    { prop: 'maintainType', label: '保养类型', type: 'select', required: true, options: [
      { label: '常规保养', value: '常规保养' }, { label: '年检', value: '年检' }, { label: '维修', value: '维修' }] },
    { prop: 'maintainDate', label: '保养日期', type: 'date', required: true },
    { prop: 'mileage', label: '保养里程', type: 'number', required: true },
    { prop: 'nextDate', label: '下次日期', type: 'date' },
    { prop: 'cost', label: '费用', type: 'number', precision: 2 },
    { prop: 'status', label: '状态', type: 'select', default: 'DONE', options: [
      { label: '已完成', value: 'DONE' }, { label: '待保养', value: 'DUE' },
      { label: '保养中', value: 'ING' }] }
  ]
}""")

simple("ScoreList", """{
  title: '调度计算留痕', url: '/api/score',
  readonly: true,
  statusOptions: [{ label: 'P1 强烈推荐', value: 'P1' }, { label: 'P2 建议派车', value: 'P2' },
    { label: 'P3 可延后', value: 'P3' }, { label: '不推荐', value: 'NONE' }],
  columns: [
    { prop: 'orderId', label: '任务ID', type: 'num' },
    { prop: 'ruleVersion', label: '规则版本', type: 'num' },
    { prop: 'totalScore', label: '综合得分', type: 'num', align: 'right' },
    { prop: 'grade', label: '等级' },
    { prop: 'factors', label: '主要影响因素', minWidth: 260 },
    { prop: 'unmet', label: '未满足条件', minWidth: 200 },
    { prop: 'improve', label: '可改进项', minWidth: 220 },
    { prop: 'createTime', label: '计算时间', type: 'time' }
  ],
  fields: []
}""")

simple("UserList", """{
  title: '用户管理', url: '/api/user',
  statusOptions: [{ label: '启用', value: '1' }, { label: '停用', value: '0' }],
  columns: [
    { prop: 'avatar', label: '头像', type: 'image', minWidth: 90 },
    { prop: 'username', label: '账号' },
    { prop: 'realName', label: '姓名' },
    { prop: 'phone', label: '手机号' },
    { prop: 'orgId', label: '单位ID', type: 'num' },
    { prop: 'status', label: '状态', type: 'status' },
    { prop: 'lastLogin', label: '最近登录', type: 'time' }
  ],
  fields: [
    { prop: 'username', label: '账号', required: true },
    { prop: 'realName', label: '姓名', required: true },
    { prop: 'phone', label: '手机号' },
    { prop: 'orgId', label: '单位ID', type: 'number' },
    { prop: 'roleId', label: '角色ID', type: 'number', required: true },
    { prop: 'status', label: '状态', type: 'select', default: 1, options: [
      { label: '启用', value: 1 }, { label: '停用', value: 0 }] }
  ]
}""")

simple("RoleList", """{
  title: '角色管理', url: '/api/role',
  columns: [
    { prop: 'roleCode', label: '角色编码' },
    { prop: 'roleName', label: '角色名称' },
    { prop: 'dataScope', label: '数据范围' },
    { prop: 'remark', label: '说明', minWidth: 240 }
  ],
  fields: [
    { prop: 'roleCode', label: '角色编码', required: true },
    { prop: 'roleName', label: '角色名称', required: true },
    { prop: 'dataScope', label: '数据范围', type: 'select', options: [
      { label: '本人 SELF', value: 'SELF' }, { label: '部门 DEPT', value: 'DEPT' },
      { label: '组织 ORG', value: 'ORG' }, { label: '全部 ALL', value: 'ALL' }] },
    { prop: 'remark', label: '说明', type: 'textarea' }
  ]
}""")

simple("MenuList", """{
  title: '菜单管理', url: '/api/menu',
  columns: [
    { prop: 'menuName', label: '菜单名称' },
    { prop: 'path', label: '路由' },
    { prop: 'icon', label: '图标' },
    { prop: 'menuType', label: '类型' },
    { prop: 'perm', label: '权限标识' },
    { prop: 'sort', label: '排序', type: 'num', align: 'right' }
  ],
  fields: [
    { prop: 'parentId', label: '上级ID', type: 'number', default: 0 },
    { prop: 'menuName', label: '菜单名称', required: true },
    { prop: 'path', label: '路由' },
    { prop: 'icon', label: '图标' },
    { prop: 'menuType', label: '类型', type: 'select', default: 'M', options: [
      { label: '菜单', value: 'M' }, { label: '按钮', value: 'B' }] },
    { prop: 'sort', label: '排序', type: 'number', default: 1 },
    { prop: 'visible', label: '是否显示', type: 'select', default: 1, options: [
      { label: '显示', value: 1 }, { label: '隐藏', value: 0 }] }
  ]
}""")

simple("OverflowList", """{
  title: '临时报满', url: '/api/overflow',
  statusOptions: [{ label: '待派单', value: 'PENDING' }, { label: '已派单', value: 'DISPATCHED' },
    { label: '已清运', value: 'DONE' }, { label: '已取消', value: 'CANCELED' }],
  columns: [
    { prop: 'reportNo', label: '上报编号' },
    { prop: 'pointId', label: '点位ID', type: 'num' },
    { prop: 'overflowLevel', label: '满溢程度' },
    { prop: 'estimatedWeight', label: '预估量(吨)', type: 'num', align: 'right' },
    { prop: 'image', label: '现场图片', type: 'image', minWidth: 100 },
    { prop: 'description', label: '说明', minWidth: 200 },
    { prop: 'urgencyScore', label: '紧急度', type: 'num', align: 'right' },
    { prop: 'reportTime', label: '上报时间', type: 'time' },
    { prop: 'status', label: '状态', type: 'status' }
  ],
  fields: [
    { prop: 'pointId', label: '收集点ID', type: 'number', required: true },
    { prop: 'overflowLevel', label: '满溢程度', type: 'select', required: true, options: [
      { label: '轻微', value: 'LIGHT' }, { label: '明显', value: 'OBVIOUS' }, { label: '严重', value: 'SERIOUS' }] },
    { prop: 'estimatedWeight', label: '预估量(吨)', type: 'number', precision: 1, required: true },
    { prop: 'image', label: '现场图片', type: 'image', required: true },
    { prop: 'description', label: '说明', type: 'textarea' }
  ]
}""")

for path, content in F.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
print("生成", len(F), "个视图")
