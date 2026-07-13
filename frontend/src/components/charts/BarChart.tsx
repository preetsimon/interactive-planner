interface BarChartProps {
  data: { label: string; value: number; color?: string }[];
  maxValue?: number;
}

export function BarChart({ data, maxValue }: BarChartProps) {
  const max = maxValue || Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="flex items-end gap-2 h-40">
      {data.map((item, i) => (
        <div key={i} className="flex flex-1 flex-col items-center gap-1">
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
            {item.value}h
          </span>
          <div className="w-full flex justify-center">
            <div
              className={`w-8 rounded-t-md transition-all duration-500 ${
                item.color || 'bg-indigo-500'
              }`}
              style={{ height: `${(item.value / max) * 120}px` }}
            />
          </div>
          <span className="text-[10px] text-gray-500 dark:text-gray-500 truncate max-w-[60px] text-center">
            {item.label}
          </span>
        </div>
      ))}
    </div>
  );
}
