interface SprintRingProps {
  currentWeek: number;
  totalWeeks: number;
  phase: string;
}

export function SprintRing({ currentWeek, totalWeeks, phase }: SprintRingProps) {
  const progress = Math.min(currentWeek / totalWeeks, 1);
  const radius = 52;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  const filled = circumference * progress;
  const size = 130;

  const phaseColors: Record<string, string> = {
    REST: '#22c55e',
    REVIEW: '#f59e0b',
    SPRINT: '#6366f1',
    CLOSED: '#64748b',
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 120 120" className="-rotate-90">
          {/* Background ring */}
          <circle
            cx="60" cy="60" r={radius}
            fill="none" stroke="currentColor" strokeWidth={strokeWidth}
            className="text-gray-100 dark:text-gray-800"
          />
          {/* Progress ring */}
          <circle
            cx="60" cy="60" r={radius}
            fill="none"
            stroke={phaseColors[phase] || '#6366f1'}
            strokeWidth={strokeWidth}
            strokeDasharray={`${filled} ${circumference - filled}`}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {currentWeek}
          </span>
          <span className="text-[10px] text-gray-400">
            of {totalWeeks} weeks
          </span>
        </div>
      </div>
      <div className="mt-2 flex items-center gap-1.5">
        <span
          className="h-2 w-2 rounded-full"
          style={{ backgroundColor: phaseColors[phase] || '#6366f1' }}
        />
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
          {phase}
        </span>
      </div>
    </div>
  );
}
