import { type LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  sparkline?: number[];
  progress?: number;
}

export function StatCard({
  title, value, subtitle, change, changeType = 'neutral', icon: Icon,
  sparkline, progress,
}: StatCardProps) {
  const changeColors = {
    positive: 'text-emerald-600 dark:text-emerald-400',
    negative: 'text-red-500 dark:text-red-400',
    neutral: 'text-gray-400 dark:text-gray-500',
  };

  const iconColor = {
    positive: 'text-emerald-500 dark:text-emerald-400',
    negative: 'text-red-400 dark:text-red-400',
    neutral: 'text-gray-400 dark:text-gray-500',
  };

  const renderSparkline = () => {
    if (!sparkline || sparkline.length < 2) return null;
    const max = Math.max(...sparkline, 1);
    const min = Math.min(...sparkline, 0);
    const range = max - min || 1;
    const w = 64;
    const h = 24;
    const points = sparkline
      .map((v, i) => `${(i / (sparkline.length - 1)) * w},${h - ((v - min) / range) * h}`)
      .join(' ');

    return (
      <svg width={w} height={h} className="mt-3">
        <polyline
          points={points}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-gray-300 dark:text-gray-600"
        />
      </svg>
    );
  };

  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-card transition-shadow hover:shadow-card-hover dark:border-gray-800/60 dark:bg-gray-900/50">
      <div className="flex items-center justify-between">
        <span className="text-[13px] font-medium text-gray-500 dark:text-gray-400">{title}</span>
        <Icon size={16} strokeWidth={1.75} className={iconColor[changeType]} />
      </div>
      <div className="mt-3">
        <span className="text-2xl font-semibold text-gray-900 dark:text-gray-100 tabular-nums">
          {value}
        </span>
        {subtitle && (
          <span className="ml-2 text-xs text-gray-400 dark:text-gray-500">{subtitle}</span>
        )}
      </div>
      {change && (
        <p className={`mt-1.5 text-xs font-medium ${changeColors[changeType]}`}>
          {change}
        </p>
      )}
      {progress !== undefined && (
        <div className="mt-3">
          <div className="h-1 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
            <div
              className="h-full rounded-full bg-gray-900 transition-all duration-700 dark:bg-gray-100"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
        </div>
      )}
      {renderSparkline()}
    </div>
  );
}
