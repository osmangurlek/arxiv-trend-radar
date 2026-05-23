import { useState, useEffect } from 'react'
import { getEntities, getEntityPapers } from '../api/client.js'
import { Search, X } from 'lucide-react'

const TYPE_BADGE = {
  method:  'bg-violet-900/50 text-violet-300 ring-1 ring-violet-700/50',
  dataset: 'bg-blue-900/50   text-blue-300   ring-1 ring-blue-700/50',
  task:    'bg-emerald-900/50 text-emerald-300 ring-1 ring-emerald-700/50',
  library: 'bg-amber-900/50  text-amber-300   ring-1 ring-amber-700/50',
}

const TABS = ['all', 'method', 'dataset', 'task', 'library']

export default function EntityExplorer() {
  const [entities,      setEntities]      = useState([])
  const [search,        setSearch]        = useState('')
  const [tab,           setTab]           = useState('all')
  const [selected,      setSelected]      = useState(null)
  const [papers,        setPapers]        = useState([])
  const [loading,       setLoading]       = useState(true)
  const [papersLoading, setPapersLoading] = useState(false)

  useEffect(() => {
    getEntities()
      .then(r => setEntities(r.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleSelect = async (entity) => {
    if (selected?.id === entity.id) { setSelected(null); return }
    setSelected(entity)
    setPapersLoading(true)
    try {
      const { data } = await getEntityPapers(entity.id)
      setPapers(data)
    } catch { setPapers([]) }
    finally { setPapersLoading(false) }
  }

  const filtered = entities.filter(e =>
    (tab === 'all' || e.type === tab) &&
    (!search || e.name.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Entity Explorer</h1>
        <p className="text-slate-500 mt-1 text-sm">Browse extracted entities and their related papers</p>
      </div>

      {/* Controls */}
      <div className="flex gap-3 flex-wrap items-center">
        <div className="relative flex-1 min-w-48 max-w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search entities…"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-violet-500/70"
          />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {TABS.map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-colors ${
                tab === t
                  ? 'bg-violet-600 text-white shadow-md shadow-violet-900/30'
                  : 'bg-slate-800 border border-slate-700 text-slate-400 hover:text-slate-200'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-5 items-start">
        {/* Grid */}
        <div className="flex-1 min-w-0">
          {loading ? (
            <div className="grid grid-cols-2 gap-2">
              {[...Array(10)].map((_, i) => <div key={i} className="h-14 bg-slate-800 rounded-xl animate-pulse" />)}
            </div>
          ) : filtered.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center">
              <p className="text-sm text-slate-500">No entities found.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {filtered.map(entity => (
                <button
                  key={entity.id}
                  onClick={() => handleSelect(entity)}
                  className={`text-left p-3.5 rounded-xl border transition-all ${
                    selected?.id === entity.id
                      ? 'bg-violet-900/15 border-violet-600/50 ring-1 ring-violet-500/20'
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <p className="text-sm font-medium text-slate-100 truncate">{entity.name}</p>
                  <span className={`inline-block mt-1.5 text-xs px-2 py-0.5 rounded-md ${TYPE_BADGE[entity.type] || 'bg-slate-800 text-slate-400'}`}>
                    {entity.type}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Detail panel */}
        {selected && (
          <div className="w-72 flex-shrink-0 bg-slate-900 border border-slate-800 rounded-xl p-5 sticky top-0">
            <div className="flex items-start justify-between mb-4">
              <div className="min-w-0 mr-2">
                <p className="text-sm font-semibold text-slate-100 leading-tight">{selected.name}</p>
                <span className={`inline-block mt-1.5 text-xs px-2 py-0.5 rounded-md ${TYPE_BADGE[selected.type]}`}>
                  {selected.type}
                </span>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="text-slate-600 hover:text-slate-400 flex-shrink-0 mt-0.5"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-500 mb-3 font-medium">
              {papersLoading ? 'Loading…' : `${papers.length} paper${papers.length !== 1 ? 's' : ''}`}
            </p>

            {papersLoading ? (
              <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-14 bg-slate-800 rounded-lg animate-pulse" />)}</div>
            ) : papers.length === 0 ? (
              <p className="text-xs text-slate-600 text-center py-6">No papers linked.</p>
            ) : (
              <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
                {papers.map(p => (
                  <div key={p.id} className="p-3 bg-slate-800/70 rounded-lg border border-slate-700/50">
                    <p className="text-xs font-medium text-slate-200 line-clamp-2 leading-relaxed">{p.title}</p>
                    {p.evidence && (
                      <p className="text-xs text-slate-500 mt-1.5 italic line-clamp-1">"{p.evidence}"</p>
                    )}
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className="text-xs text-slate-600 font-mono">{p.published_at?.slice(0, 10)}</span>
                      {p.confidence != null && (
                        <span className="text-xs text-emerald-600">{Math.round(p.confidence * 100)}%</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
