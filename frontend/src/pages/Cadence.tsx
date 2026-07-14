import { useEffect, useState } from 'react';
import { Calendar, ArrowRight, Plus } from 'lucide-react';
import { cadenceApi } from '@/services/api';
import type { Quarter } from '@/services/types';

const PHASES = ['REST', 'REVIEW', 'SPRINT', 'CLOSED'] as const;

export function Cadence() {
  const [quarter, setQuarter] = useState<Quarter | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cadenceApi.current().then(setQuarter).finally(() => setLoading(false));
  }, []);

  const daysLeft = quarter?.sprint_end
    ? Math.max(0, Math.ceil((new Date(quarter.sprint_end).getTime() - Date.now()) / 86400000))
    : null;

  const weekNum = quarter?.sprint_start
    ? Math.min(8, Math.max(1, Math.ceil(
        (Date.now() - new Date(quarter.sprint_start).getTime()) / (7 * 86400000)
      ) + 1))
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">Cadence</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Quarterly cycle — REST → REVIEW → SPRINT → CLOSED
        </p>
      </div>

      {loading ? (
        <div className="text-center text-sm text-gray-400">Loading...</div>
      ) : !quarter ? (
        <div className="rounded-xl border border-gray-100 bg-white p-6 text-center shadow-card dark:border-gray-800/60 dark:bg-gray-900/50">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">No active quarter.</p>
          <button
            onClick={async () => {
              const now = new Date();
              const q = Math.ceil((now.getMonth() + 1) / 3);
              const newQ = await cadenceApi.createQuarter({
                year: now.getFullYear(),
                quarter_num: q,
                theme: 'Q' + q,
              });
              setQuarter(newQ);
            }}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            <Plus size={16} />
            Create Current Quarter
          </button>
        </div>
      ) : (
        <>
          {/* Phase timeline */}
          <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-card dark:border-gray-800/60 dark:bg-gray-900/50">
            <h3 className="mb-4 text-[13px] font-medium text-gray-700 dark:text-gray-300">
              Q{quarter.quarter_num} {quarter.year} — {quarter.theme || 'No theme'}
            </h3>
            <div className="flex items-center gap-2">
              {PHASES.map((phase, i) => (
                <div key={phase} className="flex items-center">
                  <div
                    className={`flex h-10 items-center rounded-lg px-4 text-xs font-bold ${
                      phase === quarter.phase
                        ? 'bg-indigo-600 text-white'
                        : PHASES.indexOf(quarter.phase) > i
                        ? 'bg-gray-200 text-gray-500 dark:bg-gray-800 dark:text-gray-500'
                        : 'bg-gray-100 text-gray-400 dark:bg-gray-800/50 dark:text-gray-600'
                    }`}
                  >
                    {phase}
                  </div>
                  {i < 3 && <ArrowRight size={14} className="mx-1 text-gray-300 dark:text-gray-700" />}
                </div>
              ))}
            </div>
            <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
              {weekNum && quarter.phase === 'SPRINT'
                ? `Week ${weekNum} of 8 — ${daysLeft} days until deadline`
                : `Phase: ${quarter.phase}`}
            </p>
          </div>

          {/* Sprint dates */}
          {(quarter.sprint_start || quarter.sprint_end) && (
            <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-card dark:border-gray-800/60 dark:bg-gray-900/50">
              <h3 className="mb-3 text-[13px] font-medium text-gray-700 dark:text-gray-300">
                Sprint Timeline
              </h3>
              <div className="flex items-center gap-4 text-sm">
                <div>
                  <p className="text-gray-500 dark:text-gray-400">Start</p>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">
                    {quarter.sprint_start
                      ? new Date(quarter.sprint_start).toLocaleDateString()
                      : '—'}
                  </p>
                </div>
                <ArrowRight size={16} className="text-gray-300" />
                <div>
                  <p className="text-gray-500 dark:text-gray-400">Deadline</p>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">
                    {quarter.sprint_end
                      ? new Date(quarter.sprint_end).toLocaleDateString()
                      : '—'}
                  </p>
                </div>
                {daysLeft !== null && (
                  <span className="ml-auto rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700 dark:bg-amber-500/10 dark:text-amber-400">
                    {daysLeft} days left
                  </span>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
