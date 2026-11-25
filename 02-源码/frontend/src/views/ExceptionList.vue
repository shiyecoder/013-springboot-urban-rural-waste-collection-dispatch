<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
