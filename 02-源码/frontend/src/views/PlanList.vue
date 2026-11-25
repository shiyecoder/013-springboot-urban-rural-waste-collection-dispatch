<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
