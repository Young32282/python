<template>
  <div class="inventory-container">
    <!-- 顶部筛选栏 -->
    <el-row :gutter="16" class="filter-bar">
      <el-col :span="5">
        <el-select v-model="filters.status" placeholder="库存状态" @change="fetchInventory">
          <el-option label="全部" value="all" />
          <el-option label="预警" value="warning" />
          <el-option label="缺货" value="shortage" />
          <el-option label="快消" value="fast_moving" />
        </el-select>
      </el-col>
      <el-col :span="5">
        <el-select v-model="filters.category" placeholder="商品品类" @change="fetchInventory">
          <el-option label="全部" value="" />
          <el-option label="T恤" value="T恤" />
          <el-option label="衬衫" value="衬衫" />
          <el-option label="裤装" value="裤装" />
          <el-option label="外套" value="外套" />
          <el-option label="配饰" value="配饰" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索商品名/SKU"
          clearable
          @clear="fetchInventory"
          @keyup.enter="fetchInventory"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-col>
      <el-col :span="3">
        <el-button type="primary" @click="fetchInventory">查询</el-button>
      </el-col>
    </el-row>

    <!-- 库存表格 -->
    <el-table
      :data="inventoryList"
      :row-class-name="getRowClass"
      border
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="product_name" label="商品名" min-width="150" />
      <el-table-column prop="sku" label="SKU" width="140" />
      <el-table-column prop="category" label="品类" width="100" />
      <el-table-column prop="quantity" label="当前库存" width="100" align="center" />
      <el-table-column prop="safety_stock" label="安全线" width="100" align="center" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.status_label === '正常' ? 'success' : row.status_label === '预警' ? 'warning' : row.status_label === '快消' ? '' : 'danger'"
            :color="row.status_label === '快消' ? '#fdf6ec' : undefined"
            :style="row.status_label === '快消' ? 'color:#e6a23c;border-color:#e6a23c' : ''"
          >
            {{ row.status_label === '快消' ? '⚡快消' : row.status_label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center">
        <template #default="{ row }">
          <el-button
            type="warning"
            size="small"
            :disabled="row.status_label === '正常' && !row.is_fast_moving"
            @click="openRestockDialog(row)"
          >
            发起补货
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 空状态提示 -->
    <el-empty 
      v-if="!loading && inventoryList.length === 0" 
      description="未找到匹配的库存记录"
      style="margin-top: 40px;"
    />

    <!-- 最近补货记录 -->
    <div class="restock-history" v-if="restockHistory.length > 0">
      <h4>📦 最近补货记录</h4>
      <el-timeline>
        <el-timeline-item
          v-for="item in restockHistory"
          :key="item.id"
          :timestamp="item.created_at"
          placement="top"
          color="#67c23a"
        >
          <span class="history-text">{{ item.product_name }} 补货 <strong>{{ item.quantity }}</strong> 件</span>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 我的补货申请 -->
    <div class="my-requests" v-if="myRequests.length > 0">
      <h4>📋 我的补货申请</h4>
      <el-table :data="myRequests" size="small" stripe>
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="request_qty" label="申请数量" width="90" align="center" />
        <el-table-column prop="ai_suggest_qty" label="AI建议" width="80" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'approved' ? 'success' : 'danger'" size="small">
              {{ row.status === 'pending' ? '待审批' : row.status === 'approved' ? '已批准' : '已驳回' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申请时间" width="130">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 补货弹窗 -->
    <el-dialog v-model="dialogVisible" :title="`发起补货 - ${currentProduct.product_name}`" width="500px">
      <div class="restock-info">
        <p>当前库存：<strong>{{ currentProduct.quantity }}</strong></p>
        <p>安全库存线：<strong>{{ currentProduct.safety_stock }}</strong></p>
      </div>

      <!-- AI 建议区域 -->
      <div class="ai-suggest-area">
        <h4>AI 智能建议</h4>
        <el-skeleton :rows="2" animated v-if="aiLoading" />
        <div v-else-if="aiSuggest" class="ai-result">
          <div class="suggest-qty">建议补货：<span class="big-number">{{ aiSuggest.suggest_qty }}</span> 件</div>
          <div class="suggest-reason">{{ aiSuggest.reason }}</div>
          <div class="suggest-meta">
            <span>日均销量：{{ aiSuggest.daily_avg }}件</span>
            <span>安全周期：{{ aiSuggest.safety_days }}天</span>
            <span>当前库存：{{ aiSuggest.current_qty }}件</span>
          </div>
        </div>
        <div v-else class="ai-fallback">
          <span>AI 建议暂不可用，请手动填写数量</span>
        </div>
      </div>

      <el-form label-width="100px" style="margin-top: 16px">
        <el-form-item label="补货数量">
          <el-input-number v-model="restockQty" :min="1" :max="9999" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input type="textarea" v-model="restockReason" placeholder="备注(可选)" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRestock" :loading="submitLoading">确认补货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getInventory, createRestockRequest, getRestockRequests, getAiRestockSuggest, restockProduct, getRestockHistory } from '@/api/inventory'

const route = useRoute()

const loading = ref(false)
const inventoryList = ref([])
const dialogVisible = ref(false)
const aiLoading = ref(false)
const aiSuggest = ref(null)
const restockQty = ref(1)
const restockReason = ref('')
const submitLoading = ref(false)
const currentProduct = reactive({
  id: 0,
  product_id: 0,
  product_name: '',
  quantity: 0,
  safety_stock: 0,
})

const restockHistory = ref([])
const myRequests = ref([])

const filters = reactive({
  status: 'all',
  category: '',
  keyword: '',
})

const fetchInventory = async () => {
  loading.value = true
  try {
    const res = await getInventory(filters)
    inventoryList.value = Array.isArray(res) ? res : (res?.data || res?.items || [])
  } catch (e) {
    const detail = e.response?.data?.detail || e.message || '未知错误'
    ElMessage.error(`获取库存列表失败: ${detail}`)
    inventoryList.value = []
  } finally {
    loading.value = false
  }
}

const getRowClass = ({ row }) => {
  if (row.status_label === '缺货') return 'shortage-row'
  if (row.status_label === '预警') return 'warning-row'
  if (row.is_fast_moving) return 'fast-moving-row'
  return ''
}

const openRestockDialog = async (row) => {
  Object.assign(currentProduct, row)
  restockQty.value = 1
  restockReason.value = ''
  aiSuggest.value = null
  dialogVisible.value = true

  // 请求 AI 建议
  aiLoading.value = true
  try {
    const res = await getAiRestockSuggest(row.product_id)
    aiSuggest.value = res
    if (res && res.suggest_qty) {
      restockQty.value = res.suggest_qty
    }
  } catch (e) {
    aiSuggest.value = null
  } finally {
    aiLoading.value = false
  }
}

const submitRestock = async () => {
  submitLoading.value = true
  try {
    await createRestockRequest({
      product_id: currentProduct.product_id,
      request_qty: restockQty.value,
      reason: restockReason.value,
      ai_suggest_qty: aiSuggest.value?.suggest_qty || null,
    })
    ElMessage.success('补货申请已提交，等待区域经理审批')
    dialogVisible.value = false
    fetchInventory()
    fetchRestockHistory()
    fetchMyRequests()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '提交失败')
  } finally {
    submitLoading.value = false
  }
}

const fetchRestockHistory = async () => {
  try {
    const res = await getRestockHistory()
    restockHistory.value = Array.isArray(res) ? res : []
  } catch (e) {
    restockHistory.value = []
  }
}

const formatTime = (t) => t ? t.replace('T', ' ').slice(0, 16) : ''

const fetchMyRequests = async () => {
  try {
    const res = await getRestockRequests()
    myRequests.value = Array.isArray(res) ? res : []
  } catch {
    myRequests.value = []
  }
}

onMounted(() => {
  // 检查URL参数自动设置筛选条件
  if (route.query.status) {
    filters.status = route.query.status
  }
  fetchInventory()
  fetchRestockHistory()
  fetchMyRequests()
})
</script>

<style scoped>
.inventory-container {
  padding: 20px;
}

.filter-bar {
  margin-bottom: 20px;
}

.restock-info {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.restock-info p {
  margin: 4px 0;
  color: #606266;
}

.ai-suggest-area {
  background: #ecf5ff;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #b3d8ff;
}

.ai-suggest-area h4 {
  margin: 0 0 8px 0;
  color: #409eff;
}

.ai-result .big-number {
  font-size: 24px;
  font-weight: bold;
  color: #e6a23c;
}

.ai-result .suggest-reason {
  margin-top: 8px;
  color: #606266;
  font-size: 13px;
}

.ai-result .suggest-meta {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 16px;
}

.ai-fallback {
  color: #909399;
  font-size: 13px;
}

:deep(.warning-row) {
  background-color: #fdf6ec !important;
}

:deep(.shortage-row) {
  background-color: #fef0f0 !important;
}

:deep(.fast-moving-row) {
  background-color: #fdf6ec !important;
}

.restock-history {
  margin-top: 30px;
  padding: 16px 20px;
  background: #f0f9eb;
  border-radius: 8px;
  border: 1px solid #e1f3d8;
}

.restock-history h4 {
  margin: 0 0 12px 0;
  color: #67c23a;
  font-size: 15px;
}

.history-text {
  color: #606266;
  font-size: 14px;
}

.history-text strong {
  color: #e6a23c;
  font-size: 16px;
}

.my-requests {
  margin-top: 24px;
  padding: 16px 20px;
  background: #ecf5ff;
  border-radius: 8px;
  border: 1px solid #b3d8ff;
}
.my-requests h4 {
  margin: 0 0 12px 0;
  color: #409eff;
  font-size: 15px;
}
</style>
