/**
 * 全局时间格式化：全系统统一调用，禁止各页面自行拼接
 * @param {string|Date} v 时间值
 * @param {boolean} dateOnly 是否只显示日期
 */
export function formatTime(v, dateOnly = false) {
  if (!v) return '-'
  const s = String(v).replace('T', ' ')
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ ]?(\d{2}):(\d{2}):(\d{2})/)
  if (m) {
    return dateOnly ? `${m[1]}-${m[2]}-${m[3]}` : `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}:${m[6]}`
  }
  return s
}

export function formatDate(v) {
  return formatTime(v, true)
}

/** 状态字典 → 中文标签与颜色 */
export const STATUS_TEXT = {
  PENDING_DISPATCH: '待派车',
  ACCEPTED: '已接单',
  RUNNING: '清运中',
  PENDING_CONFIRM: '待确认',
  DONE: '已完成',
  CANCELED: '已取消',
  ABNORMAL: '异常',
  NORMAL: '正常',
  OVERFLOW: '满溢',
  DISABLED: '停用',
  IDLE: '空闲',
  BUSY: '作业中',
  MAINTAIN: '保养中',
  PENDING: '待处理',
  DISPATCHED: '已派单',
  OPEN: '待处理',
  HANDLING: '处理中',
  CLOSED: '已闭环',
  PASS: '复核通过',
  REVIEW: '待复核',
  ON: '启用',
  OFF: '停用',
  DUE: '待保养',
  ING: '保养中',
  SKIPPED: '已跳过',
  WAITING: '待执行',
  ARRIVED: '已到场'
}

export function statusText(s) {
  return STATUS_TEXT[s] || s || '-'
}

export function statusType(s) {
  if (['DONE', 'CLOSED', 'PASS', 'NORMAL', 'IDLE', 'ON'].includes(s)) return 'success'
  if (['RUNNING', 'ACCEPTED', 'PENDING_CONFIRM', 'HANDLING', 'ARRIVED', 'DISPATCHED', 'BUSY'].includes(s)) return 'primary'
  if (['PENDING_DISPATCH', 'PENDING', 'WAITING', 'DUE', 'OVERFLOW', 'REVIEW'].includes(s)) return 'warning'
  if (['ABNORMAL', 'CANCELED', 'OPEN', 'DISABLED'].includes(s)) return 'danger'
  return 'info'
}
