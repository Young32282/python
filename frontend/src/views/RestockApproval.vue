<template>
  <div>
    <h3 style="margin-bottom: 16px;">补货审批</h3>
    <el-table :data="requests" stripe v-loading="loading">
      <el-table-column prop="product_name" label="商品名" />
      <el-table-column prop="sku" label="SKU" width="120" />
      <el-table-column prop="request_qty" label="申请数量" width="100" />
      <el-table-column prop="ai_suggest_qty" label="AI建议" width="90" />
      <el-table-column prop="current_qty" label="当前库存" width="100" />
      <el-table-column prop="applicant_name" label="申请人" width="90" />
      <el-table-column label="申请时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button type="success" size="small" @click="handleApprove(row.id, 'approved')">批准</el-button>
            <el-button type="danger" size="small" @click="handleApprove(row.id, 'rejected')">驳回</el-button>
          </template>
          <span v-else style="color:#999">已处理</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRestockRequests, approveRestock } from '../api/inventory'

const requests = ref([])
const loading = ref(false)

const statusType = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info')
const statusText = (s) => ({ pending: '待审批', approved: '已批准', rejected: '已驳回' }[s] || s)
const formatTime = (t) => t ? t.replace('T', ' ').slice(0, 16) : ''

async function loadData() {
  loading.value = true
  try {
    requests.value = await getRestockRequests()
  } finally {
    loading.value = false
  }
}

async function handleApprove(id, status) {
  const action = status === 'approved' ? '批准' : '驳回'
  try {
    await ElMessageBox.confirm(`确定${action}该补货申请？`, '确认', { type: 'warning' })
    await approveRestock(id, status)
    ElMessage.success(`已${action}`)
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

onMounted(loadData)
</script>
