<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
