import { useEffect, useState } from 'react';
import { Clock, Plus, Trash2 } from 'lucide-react';
import { timeBlocksApi } from '@/services/api';
import type { TimeBlock } from '@/services/types';

export function TimeBlocks() {
  const [blocks, setBlocks] = useState<TimeBlock[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    timeBlocksApi.list().then(setBlocks).finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: string) => {
    await timeBlocksApi.remove(id);
    setBlocks((prev) => prev.filter((b) => b.id !== id));
  };

  const formatTime = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Time Blocks</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {blocks.length} blocks logged
          </p>
        </div>
      </div>

      <div className="rounded-xl border bg-white shadow-sm dark:bg-gray-900 dark:border-gray-800">
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading...</div>
        ) : blocks.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">
            No time blocks yet. Start logging your time.
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {blocks.map((block) => (
              <div
                key={block.id}
                className={`flex items-center gap-4 p-4 ${
                  block.violates_protected_window || block.violates_cutoff
                    ? 'bg-red-50 dark:bg-red-500/5'
                    : ''
                }`}
              >
                <div className="rounded-lg bg-indigo-50 p-2 dark:bg-indigo-500/10">
                  <Clock size={16} className="text-indigo-600 dark:text-indigo-400" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {formatDate(block.start_at)}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatTime(block.start_at)} — {formatTime(block.end_at)}
                    {block.notes && ` · ${block.notes}`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {block.violates_protected_window && (
                    <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-500/10 dark:text-red-400">
                      Window
                    </span>
                  )}
                  {block.violates_cutoff && (
                    <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
                      Cutoff
                    </span>
                  )}
                  <button
                    onClick={() => handleDelete(block.id)}
                    className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-red-500 dark:hover:bg-gray-800"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
