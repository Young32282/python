<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isCollapsed = ref(false)

const storeNameMap = { 1: '西湖银泰店', 2: '滨江龙湖店', 0: '总部' }
const storeName = computed(() => storeNameMap[userStore.user?.store_id] || '未知门店')
const roleNameMap = { cashier: '收银员', manager: '店长', regional: '区域经理' }
const roleName = computed(() => roleNameMap[userStore.user?.role] || '')
const pageTitle = computed(() => route.meta.title || '首页')

const menuItems = [
  { permission: 'pos', icon: 'ShoppingCart', label: 'POS收银', path: '/pos' },
  { permission: 'pos', icon: 'List', label: '订单记录', path: '/orders' },
  { permission: 'inventory', icon: 'Box', label: '库存管理', path: '/inventory' },
  { permission: 'restock_approve', icon: 'Checked', label: '补货审批', path: '/restock-approval' },
  { permission: 'members', icon: 'User', label: '会员管理', path: '/members' },
  { permission: 'dashboard', icon: 'DataLine', label: '经营看板', path: '/dashboard' }
]
const visibleMenuItems = computed(() => menuItems.filter(item => userStore.hasPermission(item.permission)))

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '72px' : '240px'" class="layout-sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">
          <el-icon :size="isCollapsed ? 26 : 30"><Shop /></el-icon>
        </div>
        <transition name="fade">
          <div v-if="!isCollapsed" class="logo-text">
            <span class="logo-title">优尚服饰</span>
            <span class="logo-subtitle">{{ storeName }}</span>
          </div>
        </transition>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="isCollapsed"
        class="sidebar-menu"
        router
      >
        <el-menu-item
          v-for="(item, index) in visibleMenuItems"
          :key="item.permission"
          :index="item.path"
          class="menu-item-animate"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.label }}</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <el-icon :size="18">
            <component :is="isCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <el-header class="layout-header">
        <div class="header-left">
          <h2 class="page-title">{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <div class="user-info">
            <div class="user-avatar">
              {{ userStore.user?.real_name?.charAt(0) || 'U' }}
            </div>
            <div class="user-detail">
              <span class="user-name">{{ userStore.user?.real_name }}</span>
              <el-tag
                size="small"
                :type="userStore.user?.role === 'manager' ? 'warning' : userStore.user?.role === 'regional' ? 'danger' : ''"
                effect="plain"
              >
                {{ roleName }}
              </el-tag>
            </div>
          </div>
          <el-button size="small" @click="handleLogout" class="logout-btn">
            <el-icon><SwitchButton /></el-icon>
            退出
          </el-button>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

.layout-sidebar {
  background: #f0f2f5;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 10;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px 18px;
  position: relative;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  transition: all var(--transition);
}
.logo-icon:hover {
  transform: scale(1.05);
}

.logo-text {
  overflow: hidden;
  white-space: nowrap;
  transition: opacity 0.2s ease;
}
.logo-title {
  display: block;
  color: var(--text);
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 1px;
}
.logo-subtitle {
  display: block;
  color: var(--text-muted);
  font-size: 11px;
  margin-top: 3px;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  flex: 1;
  background: transparent !important;
  border: none !important;
  padding: 8px 12px;
  overflow-y: auto;
  overflow-x: hidden;
  transition: padding 0.3s ease;
}

.sidebar-menu .el-menu-item {
  color: var(--text-secondary) !important;
  height: 46px;
  margin: 0 0 8px 0;
  border-radius: 10px;
  background: #fff;
  transition: all 0.25s ease;
  font-weight: 500;
  letter-spacing: 0.3px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.sidebar-menu .el-menu-item:hover {
  background: #fff !important;
  color: var(--text) !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.sidebar-menu .el-menu-item.is-active {
  background: #fff !important;
  color: #6366f1 !important;
  font-weight: 600;
  position: relative;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.sidebar-menu .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: #6366f1;
  border-radius: 0 3px 3px 0;
}

.menu-item-animate {
  animation: fadeInLeft 0.4s ease-out both;
}

.sidebar-footer {
  padding: 12px;
  transition: padding 0.3s ease;
}
.collapse-btn {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 10px;
  background: #fff;
  transition: all 0.25s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.collapse-btn:hover {
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  color: var(--text);
}

.main-container {
  background: var(--bg);
  overflow: hidden;
  transition: margin-left 0.3s ease;
}

.layout-header {
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: #fff;
  border-bottom: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
  position: relative;
  z-index: 5;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  background: var(--bg-hover);
  border-radius: var(--radius-full);
  transition: all var(--transition);
  cursor: default;
}
.user-info:hover {
  background: var(--border-light);
}

.user-avatar {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #6366f1, #818cf8);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}

.logout-btn {
  border-radius: var(--radius-sm) !important;
  font-weight: 500 !important;
  transition: all var(--transition) !important;
  background: #e8f4fd !important;
  color: #1d4ed8 !important;
  border: 1px solid #bfdbfe !important;
}
.logout-btn:hover {
  background: #dbeafe !important;
  border-color: #93c5fd !important;
  transform: translateY(-1px);
}

.layout-main {
  padding: 24px;
  overflow-y: auto;
  background: var(--bg);
  height: calc(100vh - 68px);
}

/* 页面切换动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.25s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

:deep(.el-menu--collapse .el-menu-item span) { display: none; }
</style>
