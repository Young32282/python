import request from './index'

export function login(data) {
  return request.post('/auth/login', data)
}

export function getMe() {
  return request.get('/auth/me')
}
