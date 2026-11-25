<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
