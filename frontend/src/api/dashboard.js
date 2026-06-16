import request from './index'

export function getDashboardSummary() {
  return request.get('/dashboard/summary')
}

export function getSalesTrend(days = 7) {
  return request.get('/dashboard/trend', { params: { days } })
}

export function getCategoryShare() {
  return request.get('/dashboard/category-share')
}

export function getInsight() {
  return request.get('/ai/insight')
}

export function getStoreCompare() {
  return request.get('/dashboard/store-compare')
}

export function getStoreTrends(days = 7) {
  return request.get('/dashboard/store-trends', { params: { days } })
}

export function getStoreInventoryOverview() {
  return request.get('/dashboard/store-inventory')
}
