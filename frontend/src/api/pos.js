import request from './index'

export function searchProducts(keyword) {
  return request.get('/products/search', { params: { keyword } })
}

export function identifyMember(phone) {
  return request.get('/members/identify', { params: { phone } })
}

export function getActivePromotions() {
  return request.get('/promotions/active')
}

export function createOrder(data) {
  return request.post('/orders', data)
}

export function getTodayOrders() {
  return request.get('/orders', { params: { today: 'true' } })
}

export function getOrders() {
  return request.get('/orders')
}

export function voidOrder(id) {
  return request.put(`/orders/${id}/void`)
}
