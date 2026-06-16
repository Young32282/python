<template>
  <div class="pos-container">
    <el-row :gutter="16">
      <!-- 左侧主操作区 -->
      <el-col :span="14">
        <el-card shadow="never">
          <div class="search-wrapper">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索商品名称/SKU"
              clearable
              @input="handleSearch"
              @focus="handleSearch"
              prefix-icon="Search"
            />
            <div v-if="searchResults.length > 0" class="search-dropdown">
              <div
                v-for="item in searchResults"
                :key="item.id"
                class="search-item"
                @click="addToCart(item)"
              >
                <span>{{ item.name }}</span>
                <span class="search-item-info">¥{{ item.price }} | 库存: {{ item.stock }}</span>
              </div>
            </div>
          </div>

          <el-table :data="cart" style="width: 100%; margin-top: 16px" max-height="360">
            <el-table-column prop="name" label="商品名" />
            <el-table-column label="单价" width="100">
              <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="数量" width="140">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" :precision="0" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="小计" width="100">
              <template #default="{ row }">¥{{ (row.price * row.quantity).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="70">
              <template #default="{ $index }">
                <el-button type="danger" link @click="cart.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="cart-footer">
            <span class="total-text">合计: <b>¥{{ cartTotal.toFixed(2) }}</b></span>
          </div>

          <div class="pay-section">
            <el-radio-group v-model="payMethod">
              <el-radio-button value="wechat">微信</el-radio-button>
              <el-radio-button value="alipay">支付宝</el-radio-button>
              <el-radio-button value="cash">现金</el-radio-button>
              <el-radio-button value="card">银行卡</el-radio-button>
            </el-radio-group>
            <el-button
              type="primary"
              size="large"
              style="width: 100%; margin-top: 12px"
              :disabled="cart.length === 0"
              :loading="submitting"
              @click="checkout"
            >结账</el-button>
          </div>
        </el-card>

        <!-- 店长 - 今日订单 -->
        <template v-if="user.role === 'manager'">
          <el-divider>今日订单</el-divider>
          <el-table :data="todayOrders" style="width: 100%" max-height="260">
            <el-table-column prop="order_no" label="订单号" width="160" />
            <el-table-column label="金额" width="100">
              <template #default="{ row }">¥{{ row.total_amount?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === 'completed' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'completed' ? '已完成' : '已作废' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cashier_name" label="收银员" width="90" />
            <el-table-column label="时间" width="160">
              <template #default="{ row }">{{ row.created_at }}</template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button
                  v-if="row.status === 'completed'"
                  type="danger"
                  link
                  size="small"
                  @click="handleVoid(row.id)"
                >作废</el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
      </el-col>

      <!-- 右侧辅助区 -->
      <el-col :span="10">
        <!-- 会员识别 -->
        <el-card shadow="never" class="aside-card">
          <template #header><span>会员识别</span></template>
          <div class="member-row">
            <el-input v-model="memberPhone" placeholder="输入手机号" style="flex:1" @input="handleMemberPhoneChange" />
            <el-button type="primary" @click="identifyMemberAction" :loading="memberLoading" style="margin-left:8px">识别</el-button>
          </div>
          <div v-if="member" class="member-info">
            <p>姓名: {{ member.name }}
              <el-tag size="small" style="margin-left:6px">{{ member.level }}</el-tag>
              <el-button type="danger" link size="small" @click="clearMember">清除</el-button>
            </p>
            <p>积分: {{ member.points }} | 折扣: {{ (member.discount * 10).toFixed(1) }}折</p>
          </div>
        </el-card>

        <!-- 优惠信息 -->
        <el-card shadow="never" class="aside-card">
          <template #header><span>优惠信息</span></template>
          <div class="discount-info">
            <p>原价: ¥{{ cartTotal.toFixed(2) }}</p>
            <p>优惠金额: <span class="highlight">-¥{{ discountAmount.toFixed(2) }}</span></p>
            <p class="final-price">实付金额: <b>¥{{ finalPrice.toFixed(2) }}</b></p>
          </div>
        </el-card>


        <!-- 当前优惠活动 -->
        <el-card shadow="never" class="aside-card">
          <template #header><span>📢 当前优惠活动</span></template>
          <div v-if="promotionStatus.length === 0" class="promo-empty">暂无优惠活动</div>
          <ul v-else class="promo-list">
            <li
              v-for="promo in promotionStatus"
              :key="promo.id"
              :class="{ 'promo-active': promo.active, 'promo-applied': promo.isApplied }"
            >
              <span class="promo-dot">•</span>
              <span>{{ promo.name }}</span>
              <el-tag v-if="promo.isApplied" type="success" size="small" style="margin-left:6px">✅ 生效中</el-tag>
              <el-tag v-else-if="promo.active" type="info" size="small" style="margin-left:6px">已满足</el-tag>
            </li>
          </ul>
          <div v-if="appliedDiscountLabel" class="applied-discount-label">{{ appliedDiscountLabel }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 结账成功弹窗 -->
    <el-dialog v-model="successVisible" title="结账成功" width="400px" @close="resetCart">
      <div class="success-content">
        <p>订单号: {{ orderResult?.order_no }}</p>
        <p>原价: ¥{{ orderResult?.total_amount?.toFixed(2) }}</p>
        <p>优惠: -¥{{ orderResult?.discount_amount?.toFixed(2) }}</p>
        <p class="final-price">实付金额: <b>¥{{ orderResult?.payment_amount?.toFixed(2) }}</b></p>
        <p v-if="orderResult?.upgrade_msg" class="upgrade-msg">
          🎉 {{ orderResult.upgrade_msg }}
        </p>
      </div>
      <template #footer>
        <el-button type="primary" @click="successVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../stores/user'
import {
  searchProducts,
  identifyMember,
  getActivePromotions,
  createOrder,
  getTodayOrders,
  voidOrder
} from '../api/pos'

const userStore = useUserStore()
const user = computed(() => userStore.userInfo || {})

// 搜索相关
const searchKeyword = ref('')
const searchResults = ref([])
let searchTimer = null

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(async () => {
    try {
      const res = await searchProducts(searchKeyword.value.trim())
      searchResults.value = res.data || res
    } catch {
      searchResults.value = []
    }
  }, 300)
}

// 购物车
const cart = ref([])
const payMethod = ref('wechat')

function addToCart(product) {
  const exist = cart.value.find(item => item.id === product.id)
  if (exist) {
    exist.quantity += 1
  } else {
    cart.value.push({ ...product, quantity: 1 })
  }
  searchKeyword.value = ''
  searchResults.value = []
}

const cartTotal = computed(() => {
  return cart.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

// 当前促销活动
const activePromotions = ref([])

async function loadActivePromotions() {
  try {
    const res = await getActivePromotions()
    activePromotions.value = res.data || res || []
  } catch { activePromotions.value = [] }
}

// 优惠计算 - 所有优惠互斥，取最大值（与后端逻辑一致）
const promoDiscount = computed(() => {
  const total = cartTotal.value
  if (total <= 0) return 0

  let maxDiscount = 0
  for (const promo of activePromotions.value) {
    const rules = promo.rules || {}
    if (promo.type === 'full_reduction') {
      if (total >= (rules.threshold || 0)) {
        maxDiscount = Math.max(maxDiscount, rules.reduction || 0)
      }
    } else if (promo.type === 'percentage') {
      const cat = rules.category || ''
      const disc = rules.discount || 1.0
      const catTotal = cart.value
        .filter(item => item.category === cat)
        .reduce((sum, item) => sum + item.price * item.quantity, 0)
      if (catTotal > 0) {
        const saving = catTotal * (1 - disc)
        maxDiscount = Math.max(maxDiscount, saving)
      }
    }
  }
  return maxDiscount
})

const memberDiscountAmount = computed(() => {
  if (!member.value || !member.value.discount || member.value.discount >= 1) return 0
  return cartTotal.value * (1 - member.value.discount)
})

// 互斥取最大优惠（与后端pos_service.py第107行逻辑一致）
const discountAmount = computed(() => {
  return Math.round(Math.max(promoDiscount.value, memberDiscountAmount.value) * 100) / 100
})

const finalPrice = computed(() => {
  return Math.max(0, Math.round((cartTotal.value - discountAmount.value) * 100) / 100)
})

// 判断每条促销是否对当前购物车生效，并标记最终生效的优惠
const promotionStatus = computed(() => {
  const total = cartTotal.value
  let results = []
  let maxPromoValue = 0
  let maxPromoIdx = -1

  activePromotions.value.forEach((promo, idx) => {
    const rules = promo.rules || {}
    let active = false
    let saving = 0
    if (promo.type === 'full_reduction') {
      active = total >= (rules.threshold || 0)
      if (active) saving = rules.reduction || 0
    } else if (promo.type === 'percentage') {
      const cat = rules.category || ''
      const disc = rules.discount || 1.0
      const catTotal = cart.value
        .filter(item => item.category === cat)
        .reduce((sum, item) => sum + item.price * item.quantity, 0)
      active = catTotal > 0
      if (active) saving = catTotal * (1 - disc)
    }
    if (saving > maxPromoValue) {
      maxPromoValue = saving
      maxPromoIdx = idx
    }
    results.push({ ...promo, active, saving: Math.round(saving * 100) / 100 })
  })

  // 标记最终生效的优惠：如果会员折扣更大，则没有促销被标记为"生效中"
  const memberDisc = memberDiscountAmount.value
  results = results.map((r, idx) => ({
    ...r,
    isApplied: r.active && idx === maxPromoIdx && maxPromoValue >= memberDisc
  }))

  return results
})

// 当前生效优惠的描述文本
const appliedDiscountLabel = computed(() => {
  const memberDisc = memberDiscountAmount.value
  const promoDisc = promoDiscount.value
  if (promoDisc <= 0 && memberDisc <= 0) return ''
  if (promoDisc >= memberDisc) {
    const applied = promotionStatus.value.find(p => p.isApplied)
    if (applied) return `适用优惠：${applied.name}（促销优惠 ¥${applied.saving.toFixed(2)}）`
    return ''
  } else {
    const discountFold = member.value ? (member.value.discount * 10).toFixed(1) : ''
    return `适用优惠：会员${discountFold}折（优惠 ¥${memberDisc.toFixed(2)}）`
  }
})

// 会员
const memberPhone = ref('')
const member = ref(null)
const memberLoading = ref(false)

function handleMemberPhoneChange(val) {
  if (!val || val.trim() === '') {
    member.value = null
  }
}

function clearMember() {
  member.value = null
  memberPhone.value = ''
}

async function identifyMemberAction() {
  if (!memberPhone.value) return
  memberLoading.value = true
  try {
    const res = await identifyMember(memberPhone.value)
    member.value = res.data || res
    ElMessage.success(`会员识别成功: ${member.value.name}`)
  } catch {
    ElMessage.error('未找到该会员')
    member.value = null
  } finally {
    memberLoading.value = false
  }
}

// 结账
const submitting = ref(false)
const successVisible = ref(false)
const orderResult = ref(null)

async function checkout() {
  submitting.value = true
  try {
    const payload = {
      items: cart.value.map(i => ({ product_id: i.id, quantity: i.quantity, price: i.price })),
      payment_method: payMethod.value,
      member_id: member.value?.id || null,
      discount_amount: discountAmount.value,
      total_amount: finalPrice.value
    }
    const res = await createOrder(payload)
    orderResult.value = res.data || res
    successVisible.value = true
    if (user.value.role === 'manager') loadTodayOrders()
  } catch (e) {
    ElMessage.error('结账失败: ' + (e.response?.data?.detail || '未知错误'))
  } finally {
    submitting.value = false
  }
}

function resetCart() {
  cart.value = []
  member.value = null
  memberPhone.value = ''
}

// 今日订单（店长）
const todayOrders = ref([])

async function loadTodayOrders() {
  try {
    const res = await getTodayOrders()
    todayOrders.value = res.data || res
  } catch { /* ignore */ }
}

async function handleVoid(id) {
  try {
    await ElMessageBox.confirm('确定作废该订单？', '提示', { type: 'warning' })
    await voidOrder(id)
    ElMessage.success('订单已作废')
    loadTodayOrders()
  } catch { /* cancelled */ }
}

onMounted(() => {
  if (user.value.role === 'manager') loadTodayOrders()
  loadActivePromotions()
})
</script>

<style scoped>
.pos-container {
  padding: 16px;
}
.search-wrapper {
  position: relative;
}
.search-dropdown {
  position: absolute;
  top: 40px;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  max-height: 240px;
  overflow-y: auto;
  overflow-x: hidden;
  z-index: 999;
  box-shadow: 0 2px 12px rgba(0,0,0,.1);
  padding-right: 6px;
}
.search-item {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-item:hover {
  background: #f5f7fa;
}
.search-item > span:first-child {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}
.search-item-info {
  color: #909399;
  font-size: 12px;
  white-space: nowrap;
  flex-shrink: 0;
  margin-left: 12px;
  padding-right: 4px;
}
.cart-footer {
  text-align: right;
  margin-top: 12px;
  padding: 8px 0;
  border-top: 1px solid #ebeef5;
}
.total-text {
  font-size: 16px;
}
.pay-section {
  margin-top: 16px;
}
.aside-card {
  margin-bottom: 12px;
}
.member-row {
  display: flex;
  align-items: center;
}
.member-info {
  margin-top: 10px;
  font-size: 14px;
}
.member-info p {
  margin: 4px 0;
}
.discount-info p {
  margin: 6px 0;
}
.highlight {
  color: #f56c6c;
  font-weight: bold;
}
.final-price {
  font-size: 18px;
  color: #409eff;
}
.success-content p {
  margin: 8px 0;
}
.upgrade-msg {
  color: #67c23a;
  font-weight: bold;
}
.promo-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.promo-list li {
  padding: 6px 0;
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
}
.promo-list li.promo-active {
  color: #67c23a;
}
.promo-list li.promo-applied {
  color: #67c23a;
  font-weight: bold;
}
.applied-discount-label {
  margin-top: 10px;
  padding: 8px 10px;
  background: #f0f9eb;
  border-radius: 4px;
  color: #67c23a;
  font-size: 13px;
  font-weight: bold;
}
.promo-dot {
  margin-right: 6px;
}
.promo-empty {
  color: #909399;
  font-size: 13px;
}
</style>
