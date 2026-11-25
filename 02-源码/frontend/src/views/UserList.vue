<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
