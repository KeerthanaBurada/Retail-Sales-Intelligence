import client from './client'

// Helper to build optional dataset_id query string
const qs = (datasetId) => (datasetId ? `?dataset_id=${datasetId}` : '')

export const getKPIs = (datasetId) =>
  client.get(`/api/analytics/kpis${qs(datasetId)}`)

export const getMonthlyRevenue = (datasetId) =>
  client.get(`/api/analytics/monthly-revenue${qs(datasetId)}`)

export const getTopProducts = (datasetId, limit = 10) =>
  client.get(`/api/analytics/top-products${qs(datasetId)}${datasetId ? '&' : '?'}limit=${limit}`)

export const getTopCustomers = (datasetId, limit = 10) =>
  client.get(`/api/analytics/top-customers${qs(datasetId)}${datasetId ? '&' : '?'}limit=${limit}`)

export const getRevenueByRegion = (datasetId) =>
  client.get(`/api/analytics/revenue-by-region${qs(datasetId)}`)

export const getRevenueByState = (datasetId) =>
  client.get(`/api/analytics/revenue-by-state${qs(datasetId)}`)

export const getCategoryPerformance = (datasetId) =>
  client.get(`/api/analytics/category-performance${qs(datasetId)}`)

export const getSalesTrend = (datasetId) =>
  client.get(`/api/analytics/sales-trend${qs(datasetId)}`)

export const getCustomerSegments = (datasetId) =>
  client.get(`/api/analytics/customer-segments${qs(datasetId)}`)

export const getSubcategoryPerformance = (datasetId) =>
  client.get(`/api/analytics/subcategory-performance${qs(datasetId)}`)

export const getInsights = (datasetId) =>
  client.get(`/api/analytics/insights${qs(datasetId)}`)
