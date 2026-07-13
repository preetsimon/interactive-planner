interface CategorySegment {
  label: string;
  hours: number;
  color: string;
}

interface CategoryDonutProps {
  segments: CategorySegment[];
  size?: number;
  centerLabel?: string;
}

const CENTER_COLORS = [
  '#6366f1', // indigo
  '#f59e0b', // amber
  '#22c55e', // green
  '#ef4444', // red
  '#8b5cf6', // violet
  '#06b6d4', // cyan
  '#f97316', // orange
  '#64748b', // slate
];

export function CategoryDonut({ segments, size = 140, centerLabel }: CategoryDonutProps) {
  const total = segments.reduce((sum, s) => sum + s.hours, 0) || 1;
  const radius = 45;
  const strokeWidth = 14;
  const circumference = 2 * Math.PI * radius;
  let accumulated = 0;

  return (
    <div className="flex items-center gap-5">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 100 100" className="-rotate-90">
          {/* Background ring */}
          <circle
            cx="50" cy="50" r={radius}
            fill="none" stroke="currentColor" strokeWidth={strokeWidth}
            className="text-gray-100 dark:text-gray-800"
          />
          {/* Segments */}
          {segments.map((seg, i) => {
            const pct = (seg.hours / total) * circumference;
            const dashOffset = circumference - accumulated;
            accumulated += pct;
            return (
              <circle
                key={i}
                cx="50" cy="50" r={radius}
                fill="none"
                stroke={seg.color}
                strokeWidth={strokeWidth}
                strokeDasharray={`${pct} ${circumference - pct}`}
                strokeDashoffset={dashOffset}
                strokeLinecap="round"
                className="transition-all duration-700"
              />
            );
          })}
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-gray-900 dark:text-gray-100">
            {total.toFixed(1)}
          </span>
          <span className="text-[10px] text-gray-400">
            {centerLabel || 'hours'}
          </span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-col gap-2">
        {segments.map((seg, i) => (
          <div key={i} className="flex items-center gap-2">
            <span
              className="h-2.5 w-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: seg.color }}
            />
            <span className="text-xs text-gray-600 dark:text-gray-400 min-w-[80px]">
              {seg.label}
            </span>
            <span className="text-xs font-semibold text-gray-900 dark:text-gray-200 tabular-nums">
              {seg.hours.toFixed(1)}h
            </span>
            <span className="text-[10px] text-gray-400 tabular-nums">
              {((seg.hours / total) * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
