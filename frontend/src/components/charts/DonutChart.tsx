interface DonutChartProps {
  segments: { label: string; value: number; color: string }[];
  size?: number;
}

export function DonutChart({ segments, size = 120 }: DonutChartProps) {
  const total = segments.reduce((sum, s) => sum + s.value, 0) || 1;
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  let accumulated = 0;

  return (
    <div className="flex items-center gap-4">
      <svg width={size} height={size} viewBox="0 0 100 100">
        {segments.map((seg, i) => {
          const pct = (seg.value / total) * circumference;
          const dashOffset = circumference - accumulated;
          accumulated += pct;
          return (
            <circle
              key={i}
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={seg.color}
              strokeWidth="12"
              strokeDasharray={`${pct} ${circumference - pct}`}
              strokeDashoffset={dashOffset}
              className="transition-all duration-700"
            />
          );
        })}
        <text
          x="50"
          y="50"
          textAnchor="middle"
          dominantBaseline="central"
          className="fill-gray-900 dark:fill-gray-100 text-[14px] font-bold"
        >
          {total}h
        </text>
      </svg>
      <div className="flex flex-col gap-1.5">
        {segments.map((seg, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: seg.color }} />
            <span className="text-gray-600 dark:text-gray-400">{seg.label}</span>
            <span className="font-medium text-gray-900 dark:text-gray-200">{seg.value}h</span>
          </div>
        ))}
      </div>
    </div>
  );
}
