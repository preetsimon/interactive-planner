interface HourEntry {
  day: string;
  hours: number;
  proactive: number;
  reactive: number;
}

interface WeeklyHoursChartProps {
  data: HourEntry[];
  maxHours?: number;
}

export function WeeklyHoursChart({ data, maxHours }: WeeklyHoursChartProps) {
  const max = maxHours || Math.max(...data.map((d) => d.hours), 1);
  const totalHours = data.reduce((sum, d) => sum + d.hours, 0);

  return (
    <div className="space-y-3">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          Hours This Week
        </h3>
        <span className="text-xs text-gray-400">{totalHours.toFixed(1)}h total</span>
      </div>

      <div className="flex items-end gap-1.5 h-44">
        {data.map((item, i) => {
          const proactiveHeight = (item.proactive / max) * 140;
          const reactiveHeight = (item.reactive / max) * 140;
          const totalHeight = proactiveHeight + reactiveHeight;

          return (
            <div key={i} className="flex flex-1 flex-col items-center gap-1">
              <span className="text-[10px] font-medium text-gray-500 dark:text-gray-400 tabular-nums">
                {item.hours > 0 ? `${item.hours.toFixed(1)}h` : ''}
              </span>
              <div className="w-full flex justify-center">
                <div
                  className="w-full max-w-[32px] rounded-t-sm transition-all duration-500 ease-out relative group"
                  style={{ height: `${Math.max(totalHeight, 2)}px` }}
                >
                  {/* Reactive (bottom) */}
                  {reactiveHeight > 0 && (
                    <div
                      className="absolute bottom-0 left-0 right-0 rounded-b-sm bg-amber-400 dark:bg-amber-500/70"
                      style={{ height: `${reactiveHeight}px` }}
                    />
                  )}
                  {/* Proactive (top) */}
                  {proactiveHeight > 0 && (
                    <div
                      className="absolute top-0 left-0 right-0 rounded-t-sm bg-indigo-500 dark:bg-indigo-400"
                      style={{ height: `${proactiveHeight}px` }}
                    />
                  )}
                  {/* Tooltip */}
                  <div className="absolute -top-12 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-gray-900 px-2.5 py-1.5 text-[10px] text-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100 pointer-events-none z-10">
                    <div className="font-medium">{item.day}</div>
                    <div className="text-gray-300">
                      {item.proactive}h proactive · {item.reactive}h reactive
                    </div>
                  </div>
                </div>
              </div>
              <span className="text-[10px] text-gray-500 dark:text-gray-500 font-medium">
                {item.day}
              </span>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 pt-1">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-indigo-500" />
          <span className="text-[10px] text-gray-500 dark:text-gray-400">Proactive</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-amber-400 dark:bg-amber-500/70" />
          <span className="text-[10px] text-gray-500 dark:text-gray-400">Reactive</span>
        </div>
      </div>
    </div>
  );
}
