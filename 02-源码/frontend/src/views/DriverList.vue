<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
