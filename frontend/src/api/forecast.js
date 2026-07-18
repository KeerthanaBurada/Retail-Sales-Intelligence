import client from './client'

export const trainModel = (datasetId) =>
  client.post('/api/forecast/train', { dataset_id: datasetId })

export const getPredictions = (datasetId, periods = 12) =>
  client.get(`/api/forecast/predict/${datasetId}?periods=${periods}`)

export const getForecastResults = (datasetId) =>
  client.get(`/api/forecast/results/${datasetId}`)
