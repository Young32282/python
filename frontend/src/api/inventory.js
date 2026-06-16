import request from './index'

export function getInventory(params) {
  return request.get('/inventory', { params })
}

export function createRestockRequest(data) {
  return request.post('/restock-requests', data)
}

export function getRestockRequests() {
  return request.get('/restock-requests')
}

export function approveRestock(id, status) {
  return request.put(`/restock-requests/${id}`, { status })
}

export function getAiRestockSuggest(productId) {
  return request.post('/ai/restock-suggest', { product_id: productId })
}

export function restockProduct(data) {
  return request.post('/restock', data)
}

export function getRestockHistory() {
  return request.get('/restock-history')
}
