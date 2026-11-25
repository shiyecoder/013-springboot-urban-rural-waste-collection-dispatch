<template>
  <CrudPage :cfg="cfg" />
</template>

<script setup>
import CrudPage from '@/components/CrudPage.vue'
const cfg = {
  title: '调度计算留痕', url: '/api/score',
  readonly: true,
  statusOptions: [{ label: 'P1 强烈推荐', value: 'P1' }, { label: 'P2 建议派车', value: 'P2' },
    { label: 'P3 可延后', value: 'P3' }, { label: '不推荐', value: 'NONE' }],
  columns: [
    { prop: 'orderId', label: '任务ID', type: 'num' },
    { prop: 'ruleVersion', label: '规则版本', type: 'num' },
    { prop: 'totalScore', label: '综合得分', type: 'num', align: 'right' },
    { prop: 'grade', label: '等级' },
    { prop: 'factors', label: '主要影响因素', minWidth: 260 },
    { prop: 'unmet', label: '未满足条件', minWidth: 200 },
    { prop: 'improve', label: '可改进项', minWidth: 220 },
    { prop: 'createTime', label: '计算时间', type: 'time' }
  ],
  fields: []
}
</script>
