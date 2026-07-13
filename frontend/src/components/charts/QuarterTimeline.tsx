import { Check, Circle, Clock } from 'lucide-react';

interface QuarterTimelineProps {
  phase: string;
  sprintStart?: string | null;
  sprintEnd?: string | null;
}

const PHASES = [
  { key: 'REST', label: 'REST', description: 'Recovery & reflection' },
  { key: 'REVIEW', label: 'REVIEW', description: 'Quarter retro & planning' },
  { key: 'SPRINT', label: 'SPRINT', description: '8-week execution' },
  { key: 'CLOSED', label: 'CLOSED', description: 'Ship & wrap up' },
];

export function QuarterTimeline({ phase, sprintStart, sprintEnd }: QuarterTimelineProps) {
  const currentIdx = PHASES.findIndex((p) => p.key === phase);

  const daysLeft = sprintEnd
    ? Math.max(0, Math.ceil((new Date(sprintEnd).getTime() - Date.now()) / 86400000))
    : null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          Quarter Phases
        </h3>
        {daysLeft !== null && phase === 'SPRINT' && (
          <span className="rounded-full bg-indigo-100 px-2.5 py-0.5 text-[10px] font-bold text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400">
            {daysLeft}d left
          </span>
        )}
      </div>

      {/* Timeline bar */}
      <div className="relative">
        <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-200 dark:bg-gray-800" />
        <div className="relative flex justify-between">
          {PHASES.map((p, i) => {
            const isCompleted = i < currentIdx;
            const isCurrent = i === currentIdx;
            const isFuture = i > currentIdx;

            return (
              <div key={p.key} className="flex flex-col items-center" style={{ width: '25%' }}>
                {/* Node */}
                <div
                  className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all ${
                    isCompleted
                      ? 'border-emerald-500 bg-emerald-500 text-white'
                      : isCurrent
                      ? 'border-indigo-500 bg-indigo-500 text-white shadow-lg shadow-indigo-500/25'
                      : 'border-gray-300 bg-white text-gray-400 dark:border-gray-700 dark:bg-gray-900'
                  }`}
                >
                  {isCompleted ? (
                    <Check size={14} />
                  ) : isCurrent ? (
                    <Clock size={14} />
                  ) : (
                    <Circle size={14} />
                  )}
                </div>
                {/* Label */}
                <span
                  className={`mt-2 text-[10px] font-bold ${
                    isCurrent
                      ? 'text-indigo-600 dark:text-indigo-400'
                      : isCompleted
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : 'text-gray-400 dark:text-gray-600'
                  }`}
                >
                  {p.label}
                </span>
                <span className="text-[9px] text-gray-400 dark:text-gray-600 mt-0.5 text-center">
                  {p.description}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
