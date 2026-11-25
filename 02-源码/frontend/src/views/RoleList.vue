<template>
  <div>
    <CrudPage :cfg="cfg">
      <!-- 行内扩展：为角色分配菜单（需求 8） -->
      <template #row-actions="{ row }">
        <el-button link type="warning" @click="openAssign(row)">分配菜单</el-button>
      </template>
    </CrudPage>

    <el-dialog v-model="visible" :title="'为「' + (current.roleName || '') + '」分配菜单'" width="580px">
      <div class="muted" style="margin-bottom:12px">
        勾选需要授权的菜单后保存；该角色下次登录时按最新授权动态渲染侧边栏，菜单管理项不参与授权。
      </div>
      <el-tree ref="treeRef" :data="tree" show-checkbox node-key="id" check-strictly default-expand-all
               :props="{ label: 'menuName', children: 'children' }"
               style="max-height:420px;overflow:auto;border:1px solid var(--border);border-radius:8px;padding:8px" />
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存授权</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import CrudPage from '@/components/CrudPage.vue'
import request from '@/utils/request'

const cfg = {
  title: '角色管理', url: '/api/role', rowWidth: 220,
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
}

const treeRef = ref(null)
const visible = ref(false)
const saving = ref(false)
const tree = ref([])
const current = reactive({ id: null, roleName: '' })

/** 菜单平铺列表 → 树：parentId 为 0 / 空的作根节点 */
function buildTree(list) {
  const map = new Map()
  list.forEach((m) => map.set(m.id, { ...m, children: [] }))
  const roots = []
  map.forEach((m) => {
    const pid = m.parentId || 0
    if (pid && map.has(pid)) map.get(pid).children.push(m)
    else roots.push(m)
  })
  return roots
}

async function openAssign(row) {
  current.id = row.id
  current.roleName = row.roleName
  visible.value = true
  const [menus, checked] = await Promise.all([
    request.get('/api/menu/options'),
    request.get('/api/role/' + row.id + '/menus')
  ])
  tree.value = buildTree(menus || [])
  await nextTick()
  treeRef.value?.setCheckedKeys(checked || [], false)
}

async function save() {
  saving.value = true
  try {
    const ids = treeRef.value?.getCheckedKeys(false) || []
    await request.put('/api/role/' + current.id + '/menus', { menuIds: ids })
    ElMessage.success('已保存菜单授权，共 ' + ids.length + ' 项')
    visible.value = false
  } finally {
    saving.value = false
  }
}
</script>
