import request from './index'

export function searchMembers(keyword) {
  return request.get('/members', { params: { keyword } })
}

export function getMemberDetail(id) {
  return request.get(`/members/${id}`)
}

export function getMemberOrders(id, page = 1, pageSize = 10) {
  return request.get(`/members/${id}/orders`, { params: { page, page_size: pageSize } })
}
