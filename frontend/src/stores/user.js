import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 权限配置
const ROLE_PERMISSIONS = {
  cashier: ['pos'],
  manager: ['pos', 'inventory', 'members', 'dashboard'],
  regional: ['dashboard', 'restock_approve']
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const permissions = computed(() => {
    if (!user.value) return []
    return ROLE_PERMISSIONS[user.value.role] || []
  })

  function setLogin(tokenVal, userVal) {
    token.value = tokenVal
    user.value = userVal
    localStorage.setItem('token', tokenVal)
    localStorage.setItem('user', JSON.stringify(userVal))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function hasPermission(perm) {
    return permissions.value.includes(perm)
  }

  return { token, user, isLoggedIn, permissions, setLogin, logout, hasPermission }
})
