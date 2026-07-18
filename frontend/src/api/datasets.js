import client from './client'

export const uploadDataset = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return client.post('/api/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getDatasets = () => client.get('/api/datasets')

export const getDataset = (id) => client.get(`/api/datasets/${id}`)

export const deleteDataset = (id) => client.delete(`/api/datasets/${id}`)
