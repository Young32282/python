<template>
  <div class="dashboard" v-loading="loading" element-loading-text="加载经营数据中...">
    <!-- 数据更新时间戳 -->
    <div class="data-timestamp" v-if="!loading">
      <span>数据更新时间：{{ lastUpdateTime }}</span>
      <el-button type="primary" link size="small" @click="loadData">
        刷新
      </el-button>
    </div>

    <!-- 指标卡片行 -->
    <el-row :gutter="16" class="summary-row">
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="card-title">今日销售额</div>
          <div class="card-value">¥ {{ formatNumber(summary.today_sales) }}</div>
          <div class="card-footer" :class="summary.sales_growth >= 0 ? 'growth-up' : 'growth-down'">
            {{ summary.sales_growth >= 0 ? '↑' : '↓' }}
            {{ Math.abs(summary.sales_growth * 100).toFixed(1) }}% 较昨日
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="card-title">今日订单数</div>
          <div class="card-value">{{ summary.today_orders }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="card-title">客单价</div>
          <div class="card-value">¥ {{ formatNumber(summary.avg_price) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <div class="card-title">会员消费占比</div>
          <div class="card-value">{{ (summary.member_ratio * 100).toFixed(0) }}%</div>
          <el-progress :percentage="Math.round(summary.member_ratio * 100)" :show-text="false" :stroke-width="8" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 库存预警提醒 -->
    <el-alert
      v-if="summary.shortage_count > 0 || summary.warning_count > 0"
      :title="`库存预警：${summary.shortage_count || 0}件商品缺货，${summary.warning_count || 0}件接近安全线`"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 16px"
    />
    <el-alert
      v-if="summary.fast_moving_count > 0"
      type="error"
      show-icon
      :closable="false"
      style="margin-bottom: 16px"
    >
      <template #title>
        <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
          <span>⚡ 动态预警：{{ summary.fast_moving_count }}件商品库存虽充足但消耗过快，预计不足5天</span>
          <el-button type="danger" size="small" @click="goToFastMovingRestock" style="margin-left: 16px;">
            前往补货 →
          </el-button>
        </div>
      </template>
    </el-alert>

    <!-- 图表行 -->
    <el-row :gutter="16" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>近7天销售趋势</template>
          <div ref="trendChartRef" style="height: 320px;"></div>
          <el-empty v-if="!loading && !hasTrendData" description="暂无销售趋势数据" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>品类销售占比</template>
          <div ref="pieChartRef" style="height: 320px;"></div>
          <el-empty v-if="!loading && !hasCategoryData" description="暂无品类数据" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 区域经理 - 门店对比 -->
    <el-row v-if="isRegional && storeCompareData.length > 0" :gutter="16" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <span>📊 各门店业绩对比（近7天）</span>
          </template>
          <el-table :data="storeCompareData" stripe border style="width: 100%">
            <el-table-column prop="store_name" label="门店" />
            <el-table-column label="销售额" width="150" align="right">
              <template #default="{ row }">
                <span style="font-weight:bold;color:#409eff">¥ {{ row.total_sales.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="order_count" label="订单数" width="100" align="center" />
            <el-table-column label="客单价" width="120" align="right">
              <template #default="{ row }">¥ {{ row.avg_price.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="业绩排名" width="100" align="center">
              <template #default="{ $index }">
                <el-tag :type="$index === 0 ? 'success' : 'info'" size="small">
                  {{ $index === 0 ? '🏆 第1名' : `第${$index + 1}名` }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 区域经理 - 各门店库存概况 -->
    <el-row v-if="isRegional && storeInventory.length > 0" :gutter="16" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header><span>🏪 各门店库存概况</span></template>
          <el-row :gutter="16">
            <el-col :span="12" v-for="store in storeInventory" :key="store.store_id">
              <div class="store-inv-card">
                <h4>{{ store.store_name }}</h4>
                <div class="inv-stats">
                  <span class="inv-stat normal">正常 <b>{{ store.normal_count }}</b></span>
                  <span class="inv-stat warning">预警 <b>{{ store.warning_count }}</b></span>
                  <span class="inv-stat shortage">缺货 <b>{{ store.shortage_count }}</b></span>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 区域经理 - 各门店销售趋势对比 -->
    <el-row v-if="isRegional && storeTrends.length > 0" :gutter="16" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header><span>📈 各门店销售趋势对比（近7天）</span></template>
          <div ref="storeTrendChartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI经营洞察 -->
    <el-row :gutter="16" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>AI 经营洞察</span>
              <el-button type="primary" link size="small" @click="loadInsight" :loading="insightLoading">
                刷新分析
              </el-button>
            </div>
          </template>
          <div v-if="insightLoading">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="insight" class="insight-content">
            <p v-for="(line, idx) in insightLines" :key="idx" class="insight-line">{{ line }}</p>
            <div class="insight-meta">
              <el-tag size="small" :type="insight.source === 'ai' ? 'success' : 'info'">
                {{ insight.source === 'ai' ? 'AI分析' : '规则分析' }}
              </el-tag>
              <span class="insight-time">分析时间：{{ insightTime }}</span>
            </div>
          </div>
          <el-empty v-else description="点击刷新获取经营洞察" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getDashboardSummary, getSalesTrend, getCategoryShare, getInsight, getStoreCompare, getStoreTrends, getStoreInventoryOverview } from '../api/dashboard'
import { useUserStore } from '../stores/user'

const router = useRouter()

const userStore = useUserStore()
const isRegional = computed(() => userStore.user?.role === 'regional')
const storeCompareData = ref([])
const storeTrends = ref([])
const storeInventory = ref([])

const loading = ref(false)
const lastUpdateTime = ref('')
const hasTrendData = ref(false)
const hasCategoryData = ref(false)

const summary = ref({
  today_sales: 0, today_orders: 0, avg_price: 0,
  member_ratio: 0, yesterday_sales: 0, sales_growth: 0
})

const trendChartRef = ref(null)
const pieChartRef = ref(null)
const storeTrendChartRef = ref(null)
let trendChart = null
let pieChart = null
let storeTrendChart = null

function formatNumber(num) {
  return (num || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

async function loadData() {
  loading.value = true
  try {
    const [summaryData, trendData, categoryData] = await Promise.all([
      getDashboardSummary(),
      getSalesTrend(7),
      getCategoryShare()
    ])

    summary.value = summaryData
    hasTrendData.value = Array.isArray(trendData) && trendData.length > 0
    hasCategoryData.value = Array.isArray(categoryData) && categoryData.length > 0
    await nextTick()
    setTimeout(() => {
      renderTrendChart(trendData)
      renderPieChart(categoryData)
    }, 100)

    // 区域经理加载门店对比数据
    if (isRegional.value) {
      try {
        const [compareRes, trendsRes, invRes] = await Promise.all([
          getStoreCompare(),
          getStoreTrends(7),
          getStoreInventoryOverview()
        ])
        storeCompareData.value = compareRes
        storeTrends.value = trendsRes
        storeInventory.value = invRes
      } catch(e) {
        storeCompareData.value = []
        storeTrends.value = []
        storeInventory.value = []
      }
      await nextTick()
      setTimeout(() => {
        renderStoreTrendChart()
      }, 150)
    }

    lastUpdateTime.value = new Date().toLocaleString('zh-CN', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    })
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
}

function renderTrendChart(data) {
  if (!trendChartRef.value || !data || data.length === 0) return
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  trendChart.resize()
  trendChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>销售额: ¥{c}' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)), boundaryGap: false },
    yAxis: { type: 'value', name: '销售额(元)' },
    series: [{
      type: 'line',
      data: data.map(d => d.amount),
      smooth: true,
      lineStyle: { width: 3, color: '#409EFF' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64,158,255,0.3)' },
          { offset: 1, color: 'rgba(64,158,255,0.05)' }
        ])
      },
      itemStyle: { color: '#409EFF' }
    }]
  })
}

function renderPieChart(data) {
  if (!pieChartRef.value || !data || data.length === 0) return
  if (!pieChart) {
    pieChart = echarts.init(pieChartRef.value)
  }
  pieChart.resize()
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{d}%' },
      data: data.map(d => ({ name: d.category, value: d.total_amount }))
    }]
  })
}

function handleResize() {
  trendChart?.resize()
  pieChart?.resize()
  storeTrendChart?.resize()
}

function renderStoreTrendChart() {
  if (!storeTrendChartRef.value || storeTrends.value.length === 0) return
  if (!storeTrendChart) {
    storeTrendChart = echarts.init(storeTrendChartRef.value)
  }
  storeTrendChart.resize()

  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  const series = storeTrends.value.map((store, idx) => ({
    name: store.store_name,
    type: 'line',
    smooth: true,
    data: store.trend.map(d => d.amount),
    lineStyle: { width: 2, color: colors[idx % colors.length] },
    itemStyle: { color: colors[idx % colors.length] },
  }))

  const dates = storeTrends.value[0]?.trend.map(d => d.date.slice(5)) || []

  storeTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: storeTrends.value.map(s => s.store_name), top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value', name: '销售额(元)' },
    series,
  })
}

// AI经营洞察
const insightLoading = ref(false)
const insight = ref(null)
const insightTime = ref('')

const insightLines = computed(() => {
  if (!insight.value?.content) return []
  return insight.value.content.split('\n').filter(l => l.trim()).map(line => {
    // 去除可能残留的markdown格式符号
    return line
      .replace(/\*\*(.*?)\*\*/g, '$1')  // 去除**加粗**
      .replace(/\*(.*?)\*/g, '$1')      // 去除*斜体*
      .replace(/^#{1,6}\s*/g, '')       // 去除#标题
      .replace(/^[-*+]\s+/g, '')        // 去除列表符号
      .replace(/^\d+\.\s+/g, '')        // 去除数字列表
  })
})

async function loadInsight() {
  insightLoading.value = true
  try {
    const res = await getInsight()
    insight.value = res
    insightTime.value = new Date().toLocaleString('zh-CN')
  } catch (e) {
    console.error('获取洞察失败', e)
  } finally {
    insightLoading.value = false
  }
}

function goToFastMovingRestock() {
  router.push({ path: '/inventory', query: { status: 'fast_moving' } })
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  loadData()
  loadInsight()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
  storeTrendChart?.dispose()
})
</script>

<style scoped>
.dashboard { padding: 0; }
.summary-row { margin-bottom: 0; }
.summary-card {
  text-align: center;
  border-top: 3px solid #409EFF;
  transition: transform 0.2s, box-shadow 0.2s;
}
.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.card-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.card-value { font-size: 28px; font-weight: bold; color: #303133; margin-bottom: 8px; }
.card-footer { font-size: 12px; }
.growth-up { color: #67c23a; }
.growth-down { color: #f56c6c; }

/* 卡片数值颜色区分 */
.summary-row .el-col:nth-child(1) .card-value { color: #409EFF; }
.summary-row .el-col:nth-child(2) .card-value { color: #67C23A; }
.summary-row .el-col:nth-child(3) .card-value { color: #E6A23C; }
.summary-row .el-col:nth-child(4) .card-value { color: #F56C6C; }

/* 数据更新时间戳 */
.data-timestamp {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}
.insight-content { line-height: 1.8; }
.insight-line { margin: 6px 0; color: #303133; }
.insight-meta { margin-top: 12px; display: flex; align-items: center; gap: 12px; }
.insight-time { font-size: 12px; color: #909399; }

.store-inv-card {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 8px;
}
.store-inv-card h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
}
.inv-stats {
  display: flex;
  gap: 16px;
}
.inv-stat {
  font-size: 13px;
}
.inv-stat b { font-size: 18px; margin-left: 4px; }
.inv-stat.normal { color: #67c23a; }
.inv-stat.warning { color: #e6a23c; }
.inv-stat.shortage { color: #f56c6c; }
</style>
