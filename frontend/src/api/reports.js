import client from './client'

export const generateReport = (datasetId, title, reportType) =>
  client.post('/api/reports/generate', {
    dataset_id: datasetId,
    title,
    report_type: reportType,
  })

export const getReports = () => client.get('/api/reports')

export const downloadReport = (reportId, format = 'pdf') =>
  client.get(`/api/reports/${reportId}/download?format=${format}`, {
    responseType: 'blob',
  })

export const deleteReport = (reportId) =>
  client.delete(`/api/reports/${reportId}`)
