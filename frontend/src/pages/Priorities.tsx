import { useEffect, useState } from 'react';
import { Target, Scissors, CheckCircle, Plus, X } from 'lucide-react';
import { prioritiesApi } from '@/services/api';
import type { Priority } from '@/services/types';

const trackColors: Record<string, string> = {
  TECHNICAL: 'bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400',
  LANGUAGE: 'bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400',
};

export function Priorities() {
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<{ title: string; track: 'TECHNICAL' | 'LANGUAGE'; definition_of_done: string }>({
    title: '', track: 'TECHNICAL', definition_of_done: '',
  });
  const [error, setError] = useState('');

  const load = () => {
    prioritiesApi.list().then(setPriorities).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    setError('');
    try {
      await prioritiesApi.create(form);
      setShowForm(false);
      setForm({ title: '', track: 'TECHNICAL', definition_of_done: '' });
      load();
    } catch (err: any) {
      if (err?.status === 409) {
        setError(err.detail?.message || 'Cap reached — cut or complete existing priority first');
      } else {
        setError(err?.detail || 'Failed to create priority');
      }
    }
  };

  const handleCut = async (id: string) => {
    await prioritiesApi.cut(id);
    load();
  };

  const handleComplete = async (id: string) => {
    await prioritiesApi.complete(id);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Priorities</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Max 1 active per track — subtract to add
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          {showForm ? <X size={16} /> : <Plus size={16} />}
          {showForm ? 'Cancel' : 'Add Priority'}
        </button>
      </div>

      {showForm && (
        <div className="rounded-xl border bg-white p-5 shadow-sm dark:bg-gray-900 dark:border-gray-800">
          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
              {error}
            </div>
          )}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <input
              placeholder="Priority title"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
            />
            <select
              value={form.track}
              onChange={(e) => setForm({ ...form, track: e.target.value as 'TECHNICAL' | 'LANGUAGE' })}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
            >
              <option value="TECHNICAL">TECHNICAL</option>
              <option value="LANGUAGE">LANGUAGE</option>
            </select>
            <input
              placeholder="Definition of done"
              value={form.definition_of_done}
              onChange={(e) => setForm({ ...form, definition_of_done: e.target.value })}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
            />
          </div>
          <button
            onClick={handleCreate}
            disabled={!form.title || !form.definition_of_done}
            className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            Create
          </button>
        </div>
      )}

      {loading ? (
        <div className="text-center text-sm text-gray-400">Loading...</div>
      ) : priorities.length === 0 ? (
        <div className="text-center text-sm text-gray-400">No priorities yet.</div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {priorities.map((p) => (
            <div
              key={p.id}
              className="rounded-xl border bg-white p-5 shadow-sm dark:bg-gray-900 dark:border-gray-800"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Target size={16} className="text-indigo-600 dark:text-indigo-400" />
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${trackColors[p.track]}`}>
                    {p.track}
                  </span>
                </div>
                <span
                  className={`flex items-center gap-1 text-xs ${
                    p.status === 'ACTIVE'
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : p.status === 'CUT'
                      ? 'text-gray-400'
                      : 'text-blue-600 dark:text-blue-400'
                  }`}
                >
                  {p.status === 'ACTIVE' && <CheckCircle size={14} />}
                  {p.status}
                </span>
              </div>
              <h3 className="mt-3 text-sm font-semibold text-gray-900 dark:text-gray-100">
                {p.title}
              </h3>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                DoD: {p.definition_of_done}
              </p>
              {p.status === 'ACTIVE' && (
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => handleCut(p.id)}
                    className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                  >
                    <Scissors size={14} />
                    Cut
                  </button>
                  <button
                    onClick={() => handleComplete(p.id)}
                    className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                  >
                    Complete
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
