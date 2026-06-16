<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goBack() {
  router.go(-1)
}
</script>

<template>
  <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
    <el-result
      icon="warning"
      title="无权限"
      sub-title="您的角色无权访问此页面"
    >
      <template #extra>
        <el-button type="primary" @click="goBack">返回上一页</el-button>
      </template>
    </el-result>
  </div>
</template>
