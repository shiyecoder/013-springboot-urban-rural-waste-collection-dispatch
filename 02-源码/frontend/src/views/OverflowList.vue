<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
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
}
</script>
