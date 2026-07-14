import { useMemo, useState } from 'react';

interface ActivityHeatmapProps {
  data: Record<string, number>;
  weeks?: number;
}

const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAY_LABELS = ['', 'Mon', '', 'Wed', '', 'Fri', ''];

function getLevel(count: number, max: number): number {
  if (count === 0) return 0;
  if (max <= 1) return 4;
  const ratio = count / max;
  if (ratio <= 0.25) return 1;
  if (ratio <= 0.5) return 2;
  if (ratio <= 0.75) return 3;
  return 4;
}

const CELL_CLASSES = [
  'bg-gray-100 dark:bg-gray-800',
  'bg-teal-200 dark:bg-teal-900/60',
  'bg-teal-300 dark:bg-teal-700/70',
  'bg-teal-500 dark:bg-teal-500/80',
  'bg-teal-700 dark:bg-teal-400',
];

export function ActivityHeatmap({ data, weeks = 20 }: ActivityHeatmapProps) {
  const [tooltip, setTooltip] = useState<{ x: number; y: number; date: string; count: number } | null>(null);

  const { grid, monthHeaders, maxCount } = useMemo(() => {
    const today = new Date();
    const totalDays = weeks * 7;
    const start = new Date(today);
    start.setDate(today.getDate() - totalDays + 1);
    const startDay = start.getDay();
    const offset = startDay === 0 ? 6 : startDay - 1;
    start.setDate(start.getDate() - offset);

    const columns: { date: Date; key: string }[][] = [];
    let col: { date: Date; key: string }[] = [];
    const cursor = new Date(start);
    let max = 0;

    while (cursor <= today || col.length > 0) {
      const key = cursor.toISOString().slice(0, 10);
      const count = data[key] || 0;
      if (count > max) max = count;
      col.push({ date: new Date(cursor), key });
      if (col.length === 7) {
        columns.push(col);
        col = [];
      }
      cursor.setDate(cursor.getDate() + 1);
      if (cursor > today && col.length === 0) break;
    }
    if (col.length > 0) columns.push(col);

    const months: { label: string; col: number }[] = [];
    let lastMonth = -1;
    columns.forEach((week, i) => {
      const d = week[0].date;
      const m = d.getMonth();
      if (m !== lastMonth && d.getDate() <= 7) {
        months.push({ label: MONTH_LABELS[m], col: i });
        lastMonth = m;
      }
    });

    return { grid: columns, monthHeaders: months, maxCount: max };
  }, [data, weeks]);

  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[13px] font-medium text-gray-700 dark:text-gray-300">
          Activity
        </h3>
        <div className="flex items-center gap-1.5 text-[11px] text-gray-400 dark:text-gray-500">
          <span>Less</span>
          {[0, 1, 2, 3, 4].map((level) => (
            <div
              key={level}
              className={`h-[10px] w-[10px] rounded-sm ${CELL_CLASSES[level]}`}
            />
          ))}
          <span>More</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="inline-flex gap-0">
          <div className="mr-2 flex flex-col pt-5">
            {DAY_LABELS.map((label, i) => (
              <div key={i} className="flex h-[13px] items-center">
                <span className="text-[10px] leading-none text-gray-400 dark:text-gray-500">{label}</span>
              </div>
            ))}
          </div>

          <div>
            <div className="mb-1 flex" style={{ height: '16px' }}>
              {monthHeaders.map(({ label, col }) => (
                <span
                  key={`${label}-${col}`}
                  className="absolute text-[10px] text-gray-400 dark:text-gray-500"
                  style={{ left: `${col * 13 + 32}px` }}
                >
                  {label}
                </span>
              ))}
            </div>
            <div className="flex gap-[3px]">
              {grid.map((week, wi) => (
                <div key={wi} className="flex flex-col gap-[3px]">
                  {week.map(({ key, date }) => {
                    const count = data[key] || 0;
                    const isFuture = date > new Date();
                    const level = isFuture ? -1 : getLevel(count, maxCount);
                    return (
                      <div
                        key={key}
                        className={`h-[10px] w-[10px] rounded-sm transition-colors ${
                          level === -1 ? 'bg-transparent' : CELL_CLASSES[level]
                        }`}
                        onMouseEnter={(e) => {
                          if (level >= 0) {
                            const rect = (e.target as HTMLElement).getBoundingClientRect();
                            const parent = (e.target as HTMLElement).closest('.relative')!.getBoundingClientRect();
                            setTooltip({
                              x: rect.left - parent.left + 5,
                              y: rect.top - parent.top - 36,
                              date: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }),
                              count,
                            });
                          }
                        }}
                        onMouseLeave={() => setTooltip(null)}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {tooltip && (
        <div
          className="pointer-events-none absolute z-50 rounded-md bg-gray-900 px-2.5 py-1.5 text-[11px] font-medium text-white shadow-lg dark:bg-gray-100 dark:text-gray-900"
          style={{ left: tooltip.x, top: tooltip.y, whiteSpace: 'nowrap' }}
        >
          <span className="font-semibold">{tooltip.count} action{tooltip.count !== 1 ? 's' : ''}</span>
          <span className="ml-1.5 text-gray-300 dark:text-gray-500">{tooltip.date}</span>
        </div>
      )}
    </div>
  );
}
