<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
