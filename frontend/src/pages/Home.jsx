import { useEffect, useState } from 'react'
import { getPapers, getEntities } from '../api/client.js'
import { FileText, Cpu, Database, Layers, ExternalLink } from 'lucide-react'

function StatCard({ icon: Icon, label, value, accent }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${accent}`}>
          <Icon className="w-4 h-4 text-white" />
        </div>
      </div>
      <p className="text-3xl font-bold text-slate-100">
        {value ?? <span className="text-slate-600">—</span>}
      </p>
    </div>
  )
}

function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-slate-800 rounded-xl ${className}`} />
}

export default function Home() {
  const [papers, setPapers] = useState([])
  const [entities, setEntities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getPapers(200), getEntities()])
      .then(([pr, er]) => { setPapers(pr.data); setEntities(er.data) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const byType = entities.reduce((acc, e) => { acc[e.type] = (acc[e.type] || 0) + 1; return acc }, {})

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>
        <p className="text-slate-500 mt-1 text-sm">AI/ML research trend intelligence powered by arXiv + LLM</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          [1,2,3,4].map(i => <Skeleton key={i} className="h-28" />)
        ) : (
          <>
            <StatCard icon={FileText} label="Papers"   value={papers.length}          accent="bg-violet-600" />
            <StatCard icon={Layers}   label="Entities" value={entities.length}         accent="bg-blue-600" />
            <StatCard icon={Cpu}      label="Methods"  value={byType.method ?? 0}      accent="bg-emerald-600" />
            <StatCard icon={Database} label="Datasets" value={byType.dataset ?? 0}     accent="bg-amber-600" />
          </>
        )}
      </div>

      {/* Recent Papers */}
      <div>
        <h2 className="text-base font-semibold text-slate-200 mb-4">Recent Papers</h2>
        {loading ? (
          <div className="space-y-3">{[1,2,3,4,5].map(i => <Skeleton key={i} className="h-20" />)}</div>
        ) : papers.length === 0 ? (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center">
            <FileText className="w-8 h-8 text-slate-700 mx-auto mb-3" />
            <p className="text-sm text-slate-500">No papers yet — go to <span className="text-violet-400">Ingest</span> to fetch some.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {papers.slice(0, 25).map(paper => (
              <div key={paper.id} className="group bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-4 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <a
                      href={paper.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm font-medium text-slate-100 hover:text-violet-400 transition-colors line-clamp-1 flex items-center gap-1.5"
                    >
                      {paper.title}
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 flex-shrink-0 transition-opacity" />
                    </a>
                    <p className="text-xs text-slate-500 mt-1">
                      {paper.authors?.slice(0, 3).join(', ')}{paper.authors?.length > 3 ? ' et al.' : ''}
                    </p>
                  </div>
                  <span className="text-xs text-slate-600 whitespace-nowrap font-mono">
                    {paper.published_at?.slice(0, 10)}
                  </span>
                </div>
                <div className="flex gap-1.5 mt-2.5 flex-wrap">
                  {paper.categories?.slice(0, 4).map(cat => (
                    <span key={cat} className="text-xs px-2 py-0.5 bg-slate-800 text-slate-400 rounded-md font-mono">{cat}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
