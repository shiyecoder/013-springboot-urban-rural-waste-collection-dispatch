import { reactive } from 'vue'

/** 轻量全局状态：登录人、角色、动态菜单 */
export const store = reactive({
  user: JSON.parse(localStorage.getItem('wd_user') || 'null'),
  menus: JSON.parse(localStorage.getItem('wd_menus') || '[]'),
  setLogin(user, menus) {
    this.user = user
    this.menus = menus || []
    localStorage.setItem('wd_user', JSON.stringify(user || null))
    localStorage.setItem('wd_menus', JSON.stringify(menus || []))
  },
  logout() {
    this.user = null
    this.menus = []
    localStorage.removeItem('wd_token')
    localStorage.removeItem('wd_user')
    localStorage.removeItem('wd_menus')
  }
})
