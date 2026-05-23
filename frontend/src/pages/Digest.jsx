import { useState, useEffect } from 'react'
import { generateDigest, getLatestDigest } from '../api/client.js'
import ReactMarkdown from 'react-markdown'
import { Sparkles, Loader2, FileText, AlertCircle } from 'lucide-react'

function lastMonday() {
  const d = new Date()
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  return d.toISOString().slice(0, 10)
}

export default function Digest() {
  const [weekStart, setWeekStart] = useState(lastMonday())
  const [loading,   setLoading]   = useState(false)
  const [content,   setContent]   = useState(null)
  const [weekLabel, setWeekLabel] = useState(null)
  const [error,     setError]     = useState(null)

  useEffect(() => {
    getLatestDigest()
      .then(({ data }) => { setContent(data.content); setWeekLabel(data.week_start?.slice(0, 10)) })
      .catch(() => {})
  }, [])

  const handleGenerate = async () => {
    setLoading(true); setError(null)
    try {
      const { data } = await generateDigest(weekStart)
      setContent(data.content)
      setWeekLabel(weekStart)
    } catch (err) {
      setError(err.response?.data?.detail || 'Digest generation failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Digest</h1>
        <p className="text-slate-500 mt-1 text-sm">LLM-generated weekly research trend summaries</p>
      </div>

      {/* Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex items-end gap-4 flex-wrap">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Week Start</label>
          <input
            type="date"
            value={weekStart}
            onChange={e => setWeekStart(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-violet-500/70"
          />
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm font-medium text-white transition-colors shadow-lg shadow-violet-900/30"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
          {loading ? 'Generating…' : 'Generate Digest'}
        </button>
      </div>

      {error && (
        <div className="flex items-start gap-3 bg-red-950/40 border border-red-800/60 rounded-xl p-4">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}

      {loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-violet-900/30 mb-4">
            <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
          </div>
          <p className="text-sm font-medium text-slate-200">Generating digest…</p>
          <p className="text-xs text-slate-500 mt-1">Analysing trends and writing summary with LLM</p>
        </div>
      )}

      {content && !loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          {weekLabel && (
            <div className="flex items-center gap-2 mb-6 pb-4 border-b border-slate-800">
              <FileText className="w-4 h-4 text-violet-400" />
              <span className="text-sm text-slate-400">
                Week of <span className="text-slate-200 font-semibold">{weekLabel}</span>
              </span>
            </div>
          )}
          <div className="prose prose-invert prose-sm max-w-none
            prose-headings:text-slate-100 prose-headings:font-semibold prose-headings:mt-6 prose-headings:mb-2
            prose-h1:text-lg prose-h2:text-base prose-h3:text-sm
            prose-p:text-slate-300 prose-p:leading-relaxed prose-p:my-2
            prose-li:text-slate-300 prose-li:my-0.5
            prose-ul:my-2 prose-ol:my-2
            prose-strong:text-slate-200 prose-strong:font-semibold
            prose-em:text-slate-400
            prose-hr:border-slate-800 prose-hr:my-6
            prose-code:text-violet-300 prose-code:bg-slate-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:font-mono">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>
      )}

      {!content && !loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-14 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-800 mb-4">
            <FileText className="w-5 h-5 text-slate-600" />
          </div>
          <p className="text-sm text-slate-500">No digest yet.</p>
          <p className="text-xs text-slate-600 mt-1">Select a week above and click Generate.</p>
        </div>
      )}
    </div>
  )
}
