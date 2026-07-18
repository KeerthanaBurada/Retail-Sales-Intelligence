import client from './client'

export const loginUser = (email, password) =>
  client.post('/api/auth/login', { email, password })

export const registerUser = (email, name, password) =>
  client.post('/api/auth/register', { email, name, password })

export const getProfile = () =>
  client.get('/api/auth/profile')
