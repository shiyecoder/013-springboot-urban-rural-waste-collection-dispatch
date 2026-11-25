<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
  title: '称重交接', url: '/api/weighing',
  statusOptions: [{ label: '复核通过', value: 'PASS' }, { label: '待复核', value: 'REVIEW' }],
  readonly: false,
  columns: [
    { prop: 'recordNo', label: '称重单号' },
    { prop: 'orderId', label: '任务ID', type: 'num' },
    { prop: 'inWeight', label: '进场重量', type: 'num', align: 'right' },
    { prop: 'outWeight', label: '出场重量', type: 'num', align: 'right' },
    { prop: 'netWeight', label: '净重(吨)', type: 'num', align: 'right' },
    { prop: 'disposeType', label: '处置方式' },
    { prop: 'deviation', label: '偏差(%)', type: 'num', align: 'right' },
    { prop: 'reviewStatus', label: '复核状态', type: 'status' },
    { prop: 'weighingImage', label: '称重单', type: 'image', minWidth: 100 },
    { prop: 'weighTime', label: '称重时间', type: 'time' }
  ],
  fields: [
    { prop: 'orderId', label: '任务ID', type: 'number', required: true },
    { prop: 'disposeSiteId', label: '处置场ID', type: 'number', required: true },
    { prop: 'inWeight', label: '进场重量', type: 'number', precision: 2, required: true },
    { prop: 'outWeight', label: '出场重量', type: 'number', precision: 2, required: true },
    { prop: 'netWeight', label: '净重', type: 'number', precision: 2, required: true },
    { prop: 'disposeType', label: '处置方式', type: 'select', options: [
      { label: '填埋', value: 'LAND_FILL' }, { label: '焚烧发电', value: 'INCINERATE' },
      { label: '资源化利用', value: 'RECYCLE' }] },
    { prop: 'weighingImage', label: '称重单', type: 'image' }
  ]
}
</script>
