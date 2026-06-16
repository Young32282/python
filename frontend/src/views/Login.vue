<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/auth'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const loginForm = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}
const formRef = ref(null)

// 动画相关状态
const showPassword = ref(false)
const mouseX = ref(0)
const mouseY = ref(0)
const isPurpleBlinking = ref(false)
const isBlackBlinking = ref(false)
const isTyping = ref(false)
const isLookingAtEachOther = ref(false)
const isPurplePeeking = ref(false)

// Refs for character elements
const purpleRef = ref(null)
const blackRef = ref(null)
const yellowRef = ref(null)
const orangeRef = ref(null)

// 预计算的角色位置
const purplePos = reactive({ faceX: 0, faceY: 0, bodySkew: 0 })
const blackPos = reactive({ faceX: 0, faceY: 0, bodySkew: 0 })
const orangePos = reactive({ faceX: 0, faceY: 0, bodySkew: 0 })
const yellowPos = reactive({ faceX: 0, faceY: 0, bodySkew: 0 })

// 派生状态
const pwdActive = computed(() => loginForm.password.length > 0)
const pwdVisible = computed(() => pwdActive.value && showPassword.value)
const pwdHidden = computed(() => pwdActive.value && !showPassword.value)

// 计算角色位置
function calcPos(refEl) {
  if (!refEl) return { faceX: 0, faceY: 0, bodySkew: 0 }
  const rect = refEl.getBoundingClientRect()
  const centerX = rect.left + rect.width / 2
  const centerY = rect.top + rect.height / 3
  const deltaX = mouseX.value - centerX
  const deltaY = mouseY.value - centerY
  return {
    faceX: Math.max(-15, Math.min(15, deltaX / 20)),
    faceY: Math.max(-10, Math.min(10, deltaY / 30)),
    bodySkew: Math.max(-6, Math.min(6, -deltaX / 120))
  }
}

function updatePositions() {
  const pp = calcPos(purpleRef.value)
  Object.assign(purplePos, pp)
  const bp = calcPos(blackRef.value)
  Object.assign(blackPos, bp)
  const op = calcPos(orangeRef.value)
  Object.assign(orangePos, op)
  const yp = calcPos(yellowRef.value)
  Object.assign(yellowPos, yp)
}

// 节流鼠标移动
let rafId = null
const handleMouseMove = (e) => {
  mouseX.value = e.clientX
  mouseY.value = e.clientY
  if (!rafId) {
    rafId = requestAnimationFrame(() => {
      updatePositions()
      rafId = null
    })
  }
}

onMounted(async () => {
  window.addEventListener('mousemove', handleMouseMove)
  await nextTick()
  updatePositions()
  startPurpleBlinking()
  startBlackBlinking()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  if (rafId) cancelAnimationFrame(rafId)
})

// 紫色角色眨眼动画
function startPurpleBlinking() {
  const scheduleBlink = () => {
    setTimeout(() => {
      isPurpleBlinking.value = true
      setTimeout(() => { isPurpleBlinking.value = false; scheduleBlink() }, 150)
    }, Math.random() * 4000 + 3000)
  }
  scheduleBlink()
}

// 黑色角色眨眼动画
function startBlackBlinking() {
  const scheduleBlink = () => {
    setTimeout(() => {
      isBlackBlinking.value = true
      setTimeout(() => { isBlackBlinking.value = false; scheduleBlink() }, 150)
    }, Math.random() * 4000 + 3000)
  }
  scheduleBlink()
}

// 输入时角色互相看
watch(isTyping, (val) => {
  if (val) {
    isLookingAtEachOther.value = true
    setTimeout(() => { isLookingAtEachOther.value = false }, 800)
  } else {
    isLookingAtEachOther.value = false
  }
})

// 紫色角色偷看密码
let peekTimer = null
watch([() => loginForm.password, showPassword], ([pwd, show]) => {
  if (peekTimer) { clearTimeout(peekTimer); peekTimer = null }
  if (pwd.length > 0 && show) {
    const schedulePeek = () => {
      peekTimer = setTimeout(() => {
        isPurplePeeking.value = true
        setTimeout(() => { isPurplePeeking.value = false; schedulePeek() }, 800)
      }, Math.random() * 3000 + 2000)
    }
    schedulePeek()
  } else {
    isPurplePeeking.value = false
  }
})

// 计算样式
const purpleStyle = computed(() => ({
  height: pwdHidden.value ? '440px' : '400px',
  transform: pwdVisible.value
    ? 'skewX(0deg)'
    : (isTyping.value || pwdHidden.value)
      ? `skewX(${(purplePos.bodySkew || 0) - 12}deg) translateX(40px)`
      : `skewX(${purplePos.bodySkew || 0}deg)`
}))

const purpleEyesStyle = computed(() => ({
  left: pwdVisible.value ? '20px' : isLookingAtEachOther.value ? '55px' : `${45 + purplePos.faceX}px`,
  top: pwdVisible.value ? '35px' : isLookingAtEachOther.value ? '65px' : `${40 + purplePos.faceY}px`
}))

const purplePupilStyle = computed(() => ({
  transform: pwdVisible.value
    ? `translate(${isPurplePeeking.value ? 4 : -4}px, ${isPurplePeeking.value ? 5 : -4}px)`
    : isLookingAtEachOther.value ? 'translate(3px, 4px)' : 'none'
}))

const blackStyle = computed(() => ({
  transform: pwdVisible.value
    ? 'skewX(0deg)'
    : isLookingAtEachOther.value
      ? `skewX(${(blackPos.bodySkew || 0) * 1.5 + 10}deg) translateX(20px)`
      : (isTyping.value || pwdHidden.value)
        ? `skewX(${(blackPos.bodySkew || 0) * 1.5}deg)`
        : `skewX(${blackPos.bodySkew || 0}deg)`
}))

const blackEyesStyle = computed(() => ({
  left: pwdVisible.value ? '10px' : isLookingAtEachOther.value ? '32px' : `${26 + blackPos.faceX}px`,
  top: pwdVisible.value ? '28px' : isLookingAtEachOther.value ? '12px' : `${32 + blackPos.faceY}px`
}))

const blackPupilStyle = computed(() => ({
  transform: pwdVisible.value
    ? 'translate(-4px, -4px)'
    : isLookingAtEachOther.value ? 'translate(0px, -4px)' : 'none'
}))

const orangeStyle = computed(() => ({
  transform: pwdVisible.value ? 'skewX(0deg)' : `skewX(${orangePos.bodySkew || 0}deg)`
}))

const orangeEyesStyle = computed(() => ({
  left: pwdVisible.value ? '50px' : `${82 + orangePos.faceX}px`,
  top: pwdVisible.value ? '85px' : `${90 + orangePos.faceY}px`
}))

const orangePupilStyle = computed(() => ({
  transform: pwdVisible.value ? 'translate(-5px, -4px)' : 'none'
}))

const yellowStyle = computed(() => ({
  transform: pwdVisible.value ? 'skewX(0deg)' : `skewX(${yellowPos.bodySkew || 0}deg)`
}))

const yellowEyesStyle = computed(() => ({
  left: pwdVisible.value ? '20px' : `${52 + yellowPos.faceX}px`,
  top: pwdVisible.value ? '35px' : `${40 + yellowPos.faceY}px`
}))

const yellowPupilStyle = computed(() => ({
  transform: pwdVisible.value ? 'translate(-5px, -4px)' : 'none'
}))

const yellowMouthStyle = computed(() => ({
  left: pwdVisible.value ? '10px' : `${40 + yellowPos.faceX}px`,
  top: pwdVisible.value ? '88px' : `${88 + yellowPos.faceY}px`
}))

// 登录处理
async function handleLogin() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const res = await login({ username: loginForm.username, password: loginForm.password })
      userStore.setLogin(res.access_token, res.user)
      ElMessage.success('登录成功')
      const permToRoute = { pos: '/pos', dashboard: '/dashboard', inventory: '/inventory', members: '/members', restock_approve: '/restock-approval' }
      const permissions = userStore.permissions
      let target = '/no-permission'
      for (const perm of permissions) { if (permToRoute[perm]) { target = permToRoute[perm]; break } }
      router.push(target)
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}
</script>

<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <div class="login-brand">
      <div class="brand-header">
        <div class="brand-logo">
          <el-icon :size="20"><Shop /></el-icon>
        </div>
        <span class="brand-name">优尚服饰</span>
      </div>

      <!-- 动画角色区域 -->
      <div class="characters-container">
        <div class="characters-wrapper">
          <!-- 紫色角色 -->
          <div ref="purpleRef" class="character purple-character" :style="purpleStyle">
            <div class="eyes-container" :style="purpleEyesStyle">
              <div class="eye" :class="{ blinking: isPurpleBlinking }">
                <div class="pupil" :style="purplePupilStyle"></div>
              </div>
              <div class="eye" :class="{ blinking: isPurpleBlinking }">
                <div class="pupil" :style="purplePupilStyle"></div>
              </div>
            </div>
          </div>

          <!-- 黑色角色 -->
          <div ref="blackRef" class="character black-character" :style="blackStyle">
            <div class="eyes-container" :style="blackEyesStyle">
              <div class="eye small" :class="{ blinking: isBlackBlinking }">
                <div class="pupil small" :style="blackPupilStyle"></div>
              </div>
              <div class="eye small" :class="{ blinking: isBlackBlinking }">
                <div class="pupil small" :style="blackPupilStyle"></div>
              </div>
            </div>
          </div>

          <!-- 橙色角色 -->
          <div ref="orangeRef" class="character orange-character" :style="orangeStyle">
            <div class="pupils-container" :style="orangeEyesStyle">
              <div class="pupil-only" :style="orangePupilStyle"></div>
              <div class="pupil-only" :style="orangePupilStyle"></div>
            </div>
          </div>

          <!-- 黄色角色 -->
          <div ref="yellowRef" class="character yellow-character" :style="yellowStyle">
            <div class="pupils-container" :style="yellowEyesStyle">
              <div class="pupil-only" :style="yellowPupilStyle"></div>
              <div class="pupil-only" :style="yellowPupilStyle"></div>
            </div>
            <div class="mouth" :style="yellowMouthStyle"></div>
          </div>
        </div>
      </div>

      <div class="brand-footer">
        <a href="#">隐私政策</a>
        <a href="#">服务条款</a>
        <a href="#">联系我们</a>
      </div>

      <div class="brand-decoration">
        <div class="deco-circle deco-1"></div>
        <div class="deco-circle deco-2"></div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-form-wrapper">
      <div class="form-container">
        <div class="mobile-logo">
          <div class="brand-logo">
            <el-icon :size="20"><Shop /></el-icon>
          </div>
          <span class="brand-name">优尚服饰</span>
        </div>

        <div class="form-header">
          <h1>欢迎回来</h1>
          <p>请输入您的账号信息</p>
        </div>

        <el-form ref="formRef" :model="loginForm" :rules="rules" label-width="0" size="large">
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              @focus="isTyping = true"
              @blur="isTyping = false"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              @focus="isTyping = true"
              @blur="isTyping = false"
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
              <template #suffix>
                <el-icon class="password-toggle" @click="showPassword = !showPassword">
                  <View v-if="showPassword" />
                  <Hide v-else />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>

          <div class="form-options">
            <label class="remember-label">
              <input type="checkbox" class="remember-checkbox" />
              <span>记住我</span>
            </label>
          </div>

          <el-form-item>
            <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">
              {{ loading ? '登录中...' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="test-accounts">
          <p class="accounts-title">测试账号</p>
          <div class="accounts-list">
            <span class="account-tag">cashier1</span>
            <span class="account-tag">manager1</span>
            <span class="account-tag">regional1</span>
          </div>
          <p class="accounts-hint">密码：123456</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
}

@media (min-width: 1024px) {
  .login-page { grid-template-columns: 1fr 1fr; }
}

.login-brand {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  background: linear-gradient(135deg, #6366f1, #4f46e5, #7c3aed);
  padding: 48px;
  position: relative;
  overflow: hidden;
  color: white;
}

@media (min-width: 1024px) {
  .login-brand { display: flex; }
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  position: relative;
  z-index: 10;
}

.brand-logo {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-name { letter-spacing: 2px; }

.characters-container {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
  z-index: 10;
}

.characters-wrapper {
  position: relative;
  width: 450px;
  height: 400px;
}

.character {
  position: absolute;
  bottom: 0;
  transition: all 0.7s ease-in-out;
  transform-origin: bottom center;
}

.purple-character {
  left: 70px;
  width: 180px;
  height: 400px;
  background-color: #6C3FF5;
  border-radius: 10px 10px 0 0;
  z-index: 1;
}

.black-character {
  left: 240px;
  width: 120px;
  height: 310px;
  background-color: #2D2D2D;
  border-radius: 8px 8px 0 0;
  z-index: 2;
}

.orange-character {
  left: 0;
  width: 240px;
  height: 200px;
  background-color: #FF9B6B;
  border-radius: 120px 120px 0 0;
  z-index: 3;
}

.yellow-character {
  left: 310px;
  width: 140px;
  height: 230px;
  background-color: #E8D754;
  border-radius: 70px 70px 0 0;
  z-index: 4;
}

.eyes-container {
  position: absolute;
  display: flex;
  gap: 24px;
  transition: all 0.7s ease-in-out;
}

.black-character .eyes-container { gap: 16px; }

.eye {
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: height 0.15s ease;
}

.eye.small { width: 16px; height: 16px; }
.eye.blinking { height: 2px; }

.pupil {
  width: 7px;
  height: 7px;
  background: #2D2D2D;
  border-radius: 50%;
  transition: transform 0.1s ease-out;
}

.pupil.small { width: 6px; height: 6px; }

.pupils-container {
  position: absolute;
  display: flex;
  gap: 20px;
  transition: all 0.2s ease-out;
}

.orange-character .pupils-container { gap: 24px; }
.yellow-character .pupils-container { gap: 16px; }

.pupil-only {
  width: 12px;
  height: 12px;
  background: #2D2D2D;
  border-radius: 50%;
  transition: transform 0.1s ease-out;
}

.mouth {
  position: absolute;
  width: 80px;
  height: 4px;
  background: #2D2D2D;
  border-radius: 4px;
  transition: all 0.2s ease-out;
}

.password-toggle {
  cursor: pointer;
  color: #909399;
  transition: color 0.2s;
}

.password-toggle:hover { color: #409eff; }

.brand-footer {
  display: flex;
  gap: 32px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  position: relative;
  z-index: 10;
}

.brand-footer a {
  color: inherit;
  text-decoration: none;
  transition: color 0.2s;
}

.brand-footer a:hover { color: white; }

.brand-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.deco-1 { width: 400px; height: 400px; top: -100px; right: -100px; }
.deco-2 { width: 300px; height: 300px; bottom: -50px; left: -50px; }

.login-form-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: #fff;
}

.form-container { width: 100%; max-width: 420px; }

.mobile-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 48px;
  color: #1e293b;
}

@media (min-width: 1024px) {
  .mobile-logo { display: none; }
}

.form-header { text-align: center; margin-bottom: 40px; }
.form-header h1 { font-size: 28px; font-weight: 700; color: #1e293b; margin-bottom: 8px; letter-spacing: -0.5px; }
.form-header p { font-size: 14px; color: #64748b; }

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px !important;
  background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
  transition: all 0.2s !important;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4) !important;
}

.test-accounts {
  margin-top: 32px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.accounts-title { font-size: 12px; color: #94a3b8; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }
.accounts-list { display: flex; justify-content: center; gap: 8px; margin-bottom: 8px; }

.account-tag {
  padding: 4px 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  color: #6366f1;
  font-weight: 500;
  font-family: 'SF Mono', 'Consolas', monospace;
}

.accounts-hint { font-size: 12px; color: #94a3b8; }

.remember-label { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #64748b; cursor: pointer; }
.remember-checkbox { width: 16px; height: 16px; accent-color: #6366f1; cursor: pointer; }
</style>
