<template>
  <div class="orders-container">
    <el-card shadow="never" style="width: 100%;">
      <template #header>
        <div class="card-header">
          <span>订单记录</span>
          <el-button type="primary" size="small" @click="loadOrders" :loading="loading">刷新</el-button>
        </div>
      </template>

      <el-table :data="orders" style="width: 100%" v-loading="loading" max-height="600">
        <el-table-column prop="order_no" label="订单号" min-width="160" />
        <el-table-column label="时间" min-width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="原价" min-width="90" align="right">
          <template #default="{ row }">¥{{ row.total_amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="优惠" min-width="80" align="right">
          <template #default="{ row }">
            <span v-if="row.discount_amount > 0" style="color: #f56c6c">-¥{{ row.discount_amount?.toFixed(2) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="实付金额" min-width="100" align="right">
          <template #default="{ row }">
            <b>¥{{ row.payment_amount?.toFixed(2) }}</b>
          </template>
        </el-table-column>
        <el-table-column label="支付方式" min-width="90" align="center">
          <template #default="{ row }">{{ payMethodMap[row.payment_method] || row.payment_method }}</template>
        </el-table-column>
        <el-table-column label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'danger'" size="small">
              {{ row.status === 'completed' ? '已完成' : '已作废' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cashier_name" label="收银员" min-width="90" />
        <el-table-column label="操作" min-width="110" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <button
                v-if="row.status === 'completed' && canVoid"
                class="action-btn btn-danger"
                @click="handleVoid(row)"
              >作废</button>
              <button
                class="action-btn btn-primary"
                @click="showDetail(row)"
              >详情</button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="detailVisible" title="订单详情" width="500px">
      <div v-if="currentOrder" class="order-detail">
        <p><b>订单号：</b>{{ currentOrder.order_no }}</p>
        <p><b>时间：</b>{{ formatTime(currentOrder.created_at) }}</p>
        <p><b>收银员：</b>{{ currentOrder.cashier_name }}</p>
        <p><b>支付方式：</b>{{ payMethodMap[currentOrder.payment_method] || currentOrder.payment_method }}</p>
        <p><b>状态：</b>
          <el-tag :type="currentOrder.status === 'completed' ? 'success' : 'danger'" size="small">
            {{ currentOrder.status === 'completed' ? '已完成' : '已作废' }}
          </el-tag>
        </p>
        <el-divider />
        <el-table :data="currentOrder.items" size="small">
          <el-table-column prop="product_name" label="商品" />
          <el-table-column label="单价" width="90">
            <template #default="{ row }">¥{{ row.unit_price?.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column label="小计" width="90">
            <template #default="{ row }">¥{{ row.subtotal?.toFixed(2) }}</template>
          </el-table-column>
        </el-table>
        <el-divider />
        <div class="order-summary">
          <p>原价合计：¥{{ currentOrder.total_amount?.toFixed(2) }}</p>
          <p v-if="currentOrder.discount_amount > 0" style="color: #f56c6c">
            优惠金额：-¥{{ currentOrder.discount_amount?.toFixed(2) }}
          </p>
          <p class="final-amount">实付金额：<b>¥{{ currentOrder.payment_amount?.toFixed(2) }}</b></p>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '../stores/user'
import { getOrders, voidOrder } from '../api/pos'

const userStore = useUserStore()
const user = computed(() => userStore.user || {})

// 是否有作废权限（manager / regional）
const canVoid = computed(() => {
  return ['manager', 'regional'].includes(user.value?.role)
})

const payMethodMap = {
  wechat: '微信',
  alipay: '支付宝',
  cash: '现金',
  card: '银行卡'
}

// 订单列表
const orders = ref([])
const loading = ref(false)

async function loadOrders() {
  loading.value = true
  try {
    const res = await getOrders()
    orders.value = res.data || res
  } catch (e) {
    ElMessage.error('获取订单失败: ' + (e.response?.data?.detail || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 格式化时间
function formatTime(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 作废订单
async function handleVoid(order) {
  try {
    await ElMessageBox.confirm(
      `确定作废订单 ${order.order_no}？\n作废后库存将回滚，会员积分和消费额将扣减。`,
      '确认作废',
      { type: 'warning', confirmButtonText: '确定作废', cancelButtonText: '取消' }
    )
    await voidOrder(order.id)
    ElMessage.success('订单已作废，数据已回滚')
    loadOrders()
  } catch {
    // 用户取消
  }
}

// 订单详情
const detailVisible = ref(false)
const currentOrder = ref(null)

function showDetail(order) {
  currentOrder.value = order
  detailVisible.value = true
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-container {
  padding: 16px;
  width: 100%;
  box-sizing: border-box;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.order-detail p {
  margin: 8px 0;
}
.order-summary {
  text-align: right;
}
.order-summary p {
  margin: 4px 0;
}
.final-amount {
  font-size: 16px;
  color: #409eff;
}

.action-btns {
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn {
  padding: 4px 14px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: #fff;
}

.btn-primary {
  color: #1e40af;
  border: 1px solid #93c5fd;
}
.btn-primary:hover {
  background: #eff6ff;
}

.btn-danger {
  color: #991b1b;
  border: 1px solid #fca5a5;
}
.btn-danger:hover {
  background: #fef2f2;
}
</style>
