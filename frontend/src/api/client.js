import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 15000,
})

export const getPapers = (limit = 50) =>
  api.get('/papers/', { params: { limit } })

export const getEntities = (entity_type, search) =>
  api.get('/entities/', {
    params: {
      entity_type: entity_type || undefined,
      search: search || undefined,
    },
  })

export const getEntityPapers = (id) =>
  api.get(`/entities/${id}/papers`)

export const getWeeklyTrends = (week_start, entity_type) =>
  api.get('/trends/week', { params: { week_start, entity_type } })

export const getCooccurrence = (entity_type = 'method', days = 30) =>
  api.get('/trends/cooccurrence', { params: { entity_type, days } })

export const ingestPapers = (query, limit, days = 7) =>
  api.post('/ingest', null, {
    params: { query, limit, days },
    timeout: 300000,
  })

export const generateDigest = (week_start) =>
  api.post('/digest/generate', null, {
    params: { week_start },
    timeout: 120000,
  })

export const getLatestDigest = () =>
  api.get('/digest/latest')
