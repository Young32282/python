<template>
  <div class="member-detail-page">
    <el-button @click="router.back()" style="margin-bottom: 20px">← 返回会员列表</el-button>

    <el-card v-if="member" style="margin-bottom: 20px">
      <el-row :gutter="20">
        <el-col :span="12">
          <h2 style="margin: 0 0 12px 0">{{ member.name }}</h2>
          <p><strong>手机号：</strong>{{ member.phone }}</p>
          <p><strong>注册时间：</strong>{{ member.created_at?.replace('T', ' ').slice(0, 19) }}</p>
          <p v-if="member.preferences">
            <strong>偏好品类：</strong>
            <el-tag
              v-for="tag in member.preferences.split(',')"
              :key="tag"
              size="small"
              style="margin-right: 6px; margin-top: 4px"
            >{{ tag.trim() }}</el-tag>
          </p>
        </el-col>
        <el-col :span="12">
          <div style="margin-bottom: 12px">
            <strong>当前等级：</strong>
            <el-tag :type="levelTagType[member.level]" size="large">{{ levelNames[member.level] }}</el-tag>
          </div>
          <div style="margin-bottom: 12px">
            <strong>等级进度：</strong>
            <el-progress
              :percentage="progressPercent"
              :status="member.level === 'diamond' ? 'success' : ''"
              style="margin-top: 8px"
            />
            <p style="font-size: 13px; color: #666; margin-top: 4px">
              <template v-if="member.level === 'diamond'">已达最高等级</template>
              <template v-else>距{{ levelNames[member.next_level] }}还需消费 ¥{{ member.spent_to_next?.toFixed(2) }}</template>
            </p>
          </div>
          <p><strong>当前积分：</strong>{{ member.points }} 分</p>
          <p><strong>当前折扣：</strong>{{ discountText }}</p>
        </el-col>
      </el-row>
    </el-card>

    <el-card>
      <template #header>
        <span style="font-weight: bold">消费记录</span>
      </template>
      <el-table :data="orders" stripe>
        <el-table-column prop="order_no" label="订单号" min-width="180" />
        <el-table-column label="消费金额" width="120">
          <template #default="{ row }">¥{{ row.total_amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="实付金额" width="120">
          <template #default="{ row }">¥{{ row.payment_amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="优惠金额" width="120">
          <template #default="{ row }">¥{{ row.discount_amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100" />
        <el-table-column prop="items_count" label="商品数" width="80" />
        <el-table-column label="时间" min-width="170">
          <template #default="{ row }">{{ row.created_at?.replace('T', ' ').slice(0, 19) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'danger'">
              {{ row.status === 'completed' ? '已完成' : '已作废' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="ordersTotal > 10"
        style="margin-top: 16px; justify-content: flex-end"
        layout="total, prev, pager, next"
        :total="ordersTotal"
        v-model:current-page="currentPage"
        :page-size="10"
        @current-change="loadOrders"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMemberDetail, getMemberOrders } from '../api/members'

const route = useRoute()
const router = useRouter()
const memberId = route.params.id

const member = ref(null)
const orders = ref([])
const ordersTotal = ref(0)
const currentPage = ref(1)

const levelNames = { normal: '普通', silver: '银卡', gold: '金卡', diamond: '钻石' }
const levelTagType = { normal: 'info', silver: '', gold: 'warning', diamond: 'danger' }

const progressPercent = computed(() => {
  if (!member.value) return 0
  if (member.value.level === 'diamond') return 100
  if (!member.value.next_level_threshold) return 0
  const pct = Math.round(member.value.total_spent / member.value.next_level_threshold * 100)
  return Math.min(pct, 100)
})

const discountText = computed(() => {
  if (!member.value) return ''
  const d = member.value.current_discount
  if (d === 1.0) return '无折扣'
  return `${(d * 10).toFixed(1)}折`
})

const loadDetail = async () => {
  try {
    member.value = await getMemberDetail(memberId)
  } catch (e) {
    console.error('获取会员详情失败', e)
  }
}

const loadOrders = async () => {
  try {
    const res = await getMemberOrders(memberId, currentPage.value, 10)
    orders.value = res.items
    ordersTotal.value = res.total
  } catch (e) {
    console.error('获取订单记录失败', e)
  }
}

onMounted(() => {
  loadDetail()
  loadOrders()
})
</script>

<style scoped>
.member-detail-page {
  padding: 20px;
}
</style>
