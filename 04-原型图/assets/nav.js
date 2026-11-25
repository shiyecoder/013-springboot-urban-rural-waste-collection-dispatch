// 原型公共导航：各 mock 页面通过 data 属性声明当前项，避免复制粘贴侧边栏
(function () {
  const items = [
    { g: '运营总览' },
    { k: 'dashboard', t: '环卫运营看板', i: 'i-dashboard', h: 'dashboard.html' },
    { g: '基础档案' },
    { k: 'point', t: '收集点管理', i: 'i-point', h: 'point-list.html' },
    { k: 'vehicle', t: '车辆档案', i: 'i-truck', h: '#' },
    { k: 'driver', t: '司机档案', i: 'i-driver', h: '#' },
    { k: 'route', t: '线路与处置场', i: 'i-route', h: '#' },
    { g: '调度台账' },
    { k: 'dispatch', t: '清运调度台', i: 'i-dispatch', h: 'dispatch-console.html' },
    { k: 'overflow', t: '临时报满', i: 'i-overflow', h: 'overflow-report.html' },
    { k: 'weigh', t: '称重交接', i: 'i-weigh', h: 'weighing-detail.html' },
    { k: 'exception', t: '异常处理', i: 'i-alert', h: '#' },
    { g: '分析与配置' },
    { k: 'rule', t: '调度规则配置', i: 'i-rule', h: 'rule-config.html' },
    { k: 'report', t: '统计报表', i: 'i-report', h: '#' },
    { g: '系统管理' },
    { k: 'user', t: '用户管理', i: 'i-user', h: '#' },
    { k: 'role', t: '角色管理', i: 'i-role', h: '#' }
  ];
  const root = document.querySelector('[data-nav]');
  if (!root) return;
  const cur = root.dataset.nav, title = root.dataset.title, user = root.dataset.user || '周建明', role = root.dataset.role || '运营管理员';
  let menu = '';
  items.forEach(it => {
    if (it.g) { menu += `<div class="grp">${it.g}</div>`; return; }
    menu += `<a class="${it.k === cur ? 'on' : ''}" href="${it.h}"><svg><use href="../icons.svg#${it.i}"/></svg>${it.t}</a>`;
  });
  document.body.insertAdjacentHTML('afterbegin', `
  <div class="app">
    <aside class="side">
      <div class="brand"><svg><use href="../icons.svg#i-truck"/></svg>环卫清运调度</div>
      <nav class="menu">${menu}</nav>
    </aside>
    <div class="main">
      <header class="top">
        <div class="crumb">${title.split(' / ')[0]} / <b>${title.split(' / ')[1] || ''}</b></div>
        <div class="right">
          <span class="muted">2026-10-31 星期六</span>
          <div class="bell"><svg width="18" height="18" fill="#5B6675"><use href="../icons.svg#i-bell"/></svg><span class="dot">7</span></div>
          <img class="avatar" src="../assets/avatar.png" alt="">
          <div class="who"><b>${user}</b>${role}</div>
        </div>
      </header>
      <div class="content" id="slot"></div>
    </div>
  </div>`);
  // 把页面原本的 content 内容搬进插槽
  const tpl = document.getElementById('page');
  if (tpl) document.getElementById('slot').appendChild(tpl);
})();
