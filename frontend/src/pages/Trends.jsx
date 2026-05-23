import { useState, useEffect } from 'react'
import { getWeeklyTrends, getCooccurrence } from '../api/client.js'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { RefreshCw, AlertCircle } from 'lucide-react'

const TYPES = ['method', 'dataset', 'task', 'library']

function lastMonday() {
  const d = new Date()
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  return d.toISOString().slice(0, 10)
}

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs shadow-xl">
      <p className="text-slate-300 font-medium mb-1 max-w-40 truncate">{label}</p>
      <p className="text-violet-300">{payload[0].value}</p>
    </div>
  )
}

function ChartCard({ title, data, dataKey, loading, emptyMsg, color = '#7c3aed' }) {
  const COLORS = ['#7c3aed', '#6d28d9', '#5b21b6', '#4c1d95', '#4338ca', '#3730a3']
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <h2 className="text-sm font-semibold text-slate-300 mb-5">{title}</h2>
      {loading ? (
        <div className="h-52 bg-slate-800 rounded-lg animate-pulse" />
      ) : data.length === 0 ? (
        <div className="h-52 flex items-center justify-center">
          <p className="text-xs text-slate-600">{emptyMsg}</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={210}>
          <BarChart data={data} layout="vertical" margin={{ left: 0, right: 20, top: 0, bottom: 0 }}>
            <XAxis type="number" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} width={130} axisLine={false} tickLine={false} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey={dataKey} radius={[0, 4, 4, 0]} maxBarSize={18}>
              {data.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

function truncate(str, n = 22) {
  return str.length > n ? str.slice(0, n) + '…' : str
}

export default function Trends() {
  const [weekStart,   setWeekStart]   = useState(lastMonday())
  const [entityType,  setEntityType]  = useState('method')
  const [trends,      setTrends]      = useState(null)
  const [cooc,        setCooc]        = useState([])
  const [loading,     setLoading]     = useState(false)
  const [error,       setError]       = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const [tr, co] = await Promise.all([
        getWeeklyTrends(weekStart, entityType),
        getCooccurrence(entityType, 30),
      ])
      setTrends(tr.data)
      setCooc(co.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load trends.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [weekStart, entityType])

  const topData    = (trends?.top_entities    || []).map(e => ({ name: truncate(e.name), count:  e.count  }))
  const growthData = (trends?.fastest_growing || []).filter(e => e.growth > 0).map(e => ({ name: truncate(e.name), growth: e.growth }))

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Trends</h1>
          <p className="text-slate-500 mt-1 text-sm">Weekly entity trends and co-occurrence analysis</p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-xs text-slate-300 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Controls */}
      <div className="flex gap-4 flex-wrap">
        <div>
          <label className="block text-xs text-slate-500 mb-1.5 font-medium">Week Start</label>
          <input
            type="date"
            value={weekStart}
            onChange={e => setWeekStart(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-violet-500/70"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-500 mb-1.5 font-medium">Entity Type</label>
          <select
            value={entityType}
            onChange={e => setEntityType(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-violet-500/70"
          >
            {TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
          </select>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 bg-red-950/40 border border-red-800/60 rounded-xl p-4 text-sm text-red-300">
          <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <ChartCard title="Top Entities"      data={topData}    dataKey="count"  loading={loading} emptyMsg="No data — ingest papers first." />
        <ChartCard title="Fastest Growing"   data={growthData} dataKey="growth" loading={loading} emptyMsg="Need data from 2+ weeks to show growth." color="#3b82f6" />
      </div>

      {/* Co-occurrence */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Co-occurrence (last 30 days)</h2>
        {loading ? (
          <div className="space-y-2">{[1,2,3,4,5].map(i => <div key={i} className="h-8 bg-slate-800 rounded animate-pulse" />)}</div>
        ) : cooc.length === 0 ? (
          <p className="text-xs text-slate-600 text-center py-8">No co-occurrence data — need more papers.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left py-2 pr-4 text-xs text-slate-500 font-medium">Entity A</th>
                  <th className="text-left py-2 pr-4 text-xs text-slate-500 font-medium">Entity B</th>
                  <th className="text-right py-2 text-xs text-slate-500 font-medium">Papers</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {cooc.slice(0, 15).map((row, i) => (
                  <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 pr-4 text-sm text-slate-300">{row.entity_a}</td>
                    <td className="py-2.5 pr-4 text-sm text-slate-300">{row.entity_b}</td>
                    <td className="py-2.5 text-right">
                      <span className="text-xs px-2 py-0.5 bg-violet-900/50 text-violet-300 rounded font-mono">{row.cooccurrence_count}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
