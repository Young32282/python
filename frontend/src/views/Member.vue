<template>
  <div class="member-page">
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="输入手机号或姓名搜索"
        style="width: 300px"
        @keyup.enter="handleSearch"
        clearable
      />
      <el-button type="primary" @click="handleSearch" style="margin-left: 12px">搜索</el-button>
    </div>

    <el-table
      :data="memberList"
      @row-click="goDetail"
      style="width: 100%; margin-top: 20px; cursor: pointer"
      stripe
    >
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column label="等级" width="100">
        <template #default="{ row }">
          <el-tag :type="levelTagType[row.level]">{{ levelNames[row.level] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="points" label="积分" width="100" />
      <el-table-column label="累计消费" width="140">
        <template #default="{ row }">
          ¥{{ row.total_spent?.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="total_orders" label="订单数" width="100" />
      <el-table-column label="注册时间" min-width="180">
        <template #default="{ row }">
          {{ row.created_at?.replace('T', ' ').slice(0, 19) }}
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { searchMembers } from '../api/members'

const router = useRouter()
const keyword = ref('')
const memberList = ref([])

const levelNames = { normal: '普通', silver: '银卡', gold: '金卡', diamond: '钻石' }
const levelTagType = { normal: 'info', silver: '', gold: 'warning', diamond: 'danger' }

const handleSearch = async () => {
  try {
    memberList.value = await searchMembers(keyword.value)
  } catch (e) {
    console.error('搜索会员失败', e)
  }
}

const goDetail = (row) => {
  router.push(`/members/${row.id}`)
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.member-page {
  padding: 20px;
}
.search-bar {
  display: flex;
  align-items: center;
}
</style>
