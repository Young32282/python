import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

import Login from '../views/Login.vue'
import Layout from '../components/Layout.vue'
import POS from '../views/POS.vue'
import Inventory from '../views/Inventory.vue'
import RestockApproval from '../views/RestockApproval.vue'
import Member from '../views/Member.vue'
import MemberDetail from '../views/MemberDetail.vue'
import Dashboard from '../views/Dashboard.vue'
import NoPermission from '../views/NoPermission.vue'
import Orders from '../views/Orders.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: 'pos',
        name: 'POS',
        component: POS,
        meta: { permission: 'pos', title: 'POS收银' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: Orders,
        meta: { permission: 'pos', title: '订单记录' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: Inventory,
        meta: { permission: 'inventory', title: '库存管理' }
      },
      {
        path: 'restock-approval',
        name: 'RestockApproval',
        component: RestockApproval,
        meta: { permission: 'restock_approve', title: '补货审批' }
      },
      {
        path: 'members',
        name: 'Member',
        component: Member,
        meta: { permission: 'members', title: '会员管理' }
      },
      {
        path: 'members/:id',
        name: 'MemberDetail',
        component: MemberDetail,
        meta: { permission: 'members', title: '会员详情' }
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { permission: 'dashboard', title: '经营看板' }
      }
    ]
  },
  {
    path: '/no-permission',
    name: 'NoPermission',
    component: NoPermission
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 根据角色获取默认首页路径
function getDefaultRoute(permissions) {
  const permToRoute = {
    pos: '/pos',
    dashboard: '/dashboard',
    inventory: '/inventory',
    members: '/members',
    restock_approve: '/restock-approval'
  }
  for (const perm of permissions) {
    if (permToRoute[perm]) {
      return permToRoute[perm]
    }
  }
  return '/no-permission'
}

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 如果去登录页且已登录，跳到默认页
  if (to.path === '/login' && userStore.isLoggedIn) {
    next(getDefaultRoute(userStore.permissions))
    return
  }

  // 如果未登录且不是去登录页，跳到登录
  if (!userStore.isLoggedIn && to.path !== '/login') {
    next('/login')
    return
  }

  // 如果是根路径，重定向到默认页
  if (to.path === '/' && userStore.isLoggedIn) {
    next(getDefaultRoute(userStore.permissions))
    return
  }

  // 检查权限
  if (to.meta.permission && !userStore.hasPermission(to.meta.permission)) {
    next('/no-permission')
    return
  }

  next()
})

export default router
