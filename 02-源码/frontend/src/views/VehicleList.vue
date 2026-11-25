<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
