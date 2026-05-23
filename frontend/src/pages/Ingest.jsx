import { useState } from 'react'
import { ingestPapers } from '../api/client.js'
import { Download, Loader2, CheckCircle, AlertCircle, Zap } from 'lucide-react'

export default function Ingest() {
  const [query, setQuery]   = useState('')
  const [limit, setLimit]   = useState(5)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError]   = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true); setResult(null); setError(null)
    try {
      const { data } = await ingestPapers(query.trim(), limit)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Ingestion failed. Check server logs.')
    } finally {
      setLoading(false)
    }
  }

  const suggestions = ['retrieval augmented generation', 'large language models', 'vision transformer', 'diffusion models', 'reinforcement learning']

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Ingest Papers</h1>
        <p className="text-slate-500 mt-1 text-sm">Fetch papers from arXiv and extract entities with LLM in parallel</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Search Query</label>
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="e.g. retrieval augmented generation"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/70 focus:border-violet-500/50 transition-all"
            />
          </div>

          {/* Suggestions */}
          <div className="flex gap-2 flex-wrap">
            {suggestions.map(s => (
              <button
                key={s}
                type="button"
                onClick={() => setQuery(s)}
                className="text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-400 hover:text-slate-200 rounded-lg transition-colors"
              >
                {s}
              </button>
            ))}
          </div>

          <div className="flex items-end gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Max Papers</label>
              <input
                type="number"
                value={limit}
                onChange={e => setLimit(Math.max(1, Math.min(50, Number(e.target.value))))}
                min={1} max={50}
                className="w-28 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-violet-500/70 transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="flex items-center gap-2 px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm font-medium text-white transition-colors shadow-lg shadow-violet-900/30"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              {loading ? 'Ingesting…' : 'Start Ingestion'}
            </button>
          </div>
        </form>

        {loading && (
          <div className="mt-2 p-4 bg-slate-800/60 border border-slate-700 rounded-xl flex items-center gap-3">
            <div className="relative flex-shrink-0">
              <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
            </div>
            <div>
              <p className="text-sm text-slate-200 font-medium">Processing…</p>
              <p className="text-xs text-slate-500 mt-0.5">Fetching arXiv + running entity extraction & classification in parallel</p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="bg-emerald-950/40 border border-emerald-800/60 rounded-xl p-4 flex items-center gap-3">
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <p className="text-sm text-emerald-300 font-medium">{result.message}</p>
          </div>

          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-violet-400" />
            <h2 className="text-base font-semibold text-slate-200">Ingested Papers</h2>
          </div>
          <div className="space-y-2">
            {result.papers?.map(p => (
              <div key={p.arxiv_id} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                <p className="text-sm font-medium text-slate-100 line-clamp-2">{p.title}</p>
                <div className="flex gap-4 mt-2">
                  <span className="text-xs font-mono text-violet-400 truncate">{p.arxiv_id}</span>
                  <span className="text-xs text-slate-500 whitespace-nowrap">{p.published_at?.slice(0, 10)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
