import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '环卫运营看板' } },
      { path: 'point', component: () => import('@/views/PointList.vue'), meta: { title: '收集点管理' } },
      { path: 'vehicle', component: () => import('@/views/VehicleList.vue'), meta: { title: '车辆档案' } },
      { path: 'driver', component: () => import('@/views/DriverList.vue'), meta: { title: '司机档案' } },
      { path: 'route', component: () => import('@/views/RouteList.vue'), meta: { title: '线路与处置场' } },
      { path: 'plan', component: () => import('@/views/PlanList.vue'), meta: { title: '周期计划' } },
      { path: 'dispatch', component: () => import('@/views/DispatchConsole.vue'), meta: { title: '清运调度台' } },
      { path: 'dispatch/:id', component: () => import('@/views/DispatchDetail.vue'), meta: { title: '清运任务详情' } },
      { path: 'overflow', component: () => import('@/views/OverflowList.vue'), meta: { title: '临时报满' } },
      { path: 'weighing', component: () => import('@/views/WeighingList.vue'), meta: { title: '称重交接' } },
      { path: 'exception', component: () => import('@/views/ExceptionList.vue'), meta: { title: '异常处理' } },
      { path: 'maintenance', component: () => import('@/views/MaintenanceList.vue'), meta: { title: '车辆保养' } },
      { path: 'rule', component: () => import('@/views/RuleConfig.vue'), meta: { title: '调度规则配置' } },
      { path: 'score', component: () => import('@/views/ScoreList.vue'), meta: { title: '计算留痕' } },
      { path: 'report', component: () => import('@/views/Report.vue'), meta: { title: '统计报表' } },
      { path: 'user', component: () => import('@/views/UserList.vue'), meta: { title: '用户管理' } },
      { path: 'role', component: () => import('@/views/RoleList.vue'), meta: { title: '角色管理' } },
      { path: 'menu', component: () => import('@/views/MenuList.vue'), meta: { title: '菜单管理' } },
      { path: 'profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人中心' } },
      { path: 'my-task', component: () => import('@/views/MyTasks.vue'), meta: { title: '我的任务' } }
    ]
  }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  if (to.meta && to.meta.public) return true
  const token = localStorage.getItem('wd_token')
  if (!token) return '/login'
  return true
})

export default router
