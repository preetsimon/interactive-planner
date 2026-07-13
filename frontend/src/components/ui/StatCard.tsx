import { type LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  sparkline?: number[];
  progress?: number; // 0-100
}

export function StatCard({
  title, value, subtitle, change, changeType = 'neutral', icon: Icon,
  sparkline, progress,
}: StatCardProps) {
  const changeColors = {
    positive: 'text-emerald-600 dark:text-emerald-400',
    negative: 'text-red-600 dark:text-red-400',
    neutral: 'text-gray-500 dark:text-gray-400',
  };

  const iconBg = {
    positive: 'bg-emerald-50 dark:bg-emerald-500/10',
    negative: 'bg-red-50 dark:bg-red-500/10',
    neutral: 'bg-indigo-50 dark:bg-indigo-500/10',
  };

  const iconColor = {
    positive: 'text-emerald-600 dark:text-emerald-400',
    negative: 'text-red-600 dark:text-red-400',
    neutral: 'text-indigo-600 dark:text-indigo-400',
  };

  // Mini sparkline SVG
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
      <svg width={w} height={h} className="mt-2">
        <polyline
          points={points}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-indigo-400 dark:text-indigo-500"
        />
      </svg>
    );
  };

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm dark:bg-gray-900 dark:border-gray-800">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</span>
        <div className={`rounded-lg p-2 ${iconBg[changeType]}`}>
          <Icon size={16} className={iconColor[changeType]} />
        </div>
      </div>
      <div className="mt-2">
        <span className="text-2xl font-bold text-gray-900 dark:text-gray-100 tabular-nums">
          {value}
        </span>
        {subtitle && (
          <span className="ml-2 text-xs text-gray-400">{subtitle}</span>
        )}
      </div>
      {change && (
        <p className={`mt-1 text-xs font-medium ${changeColors[changeType]}`}>
          {change}
        </p>
      )}
      {progress !== undefined && (
        <div className="mt-3">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
            <div
              className="h-full rounded-full bg-indigo-500 transition-all duration-700"
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
        </div>
      )}
      {renderSparkline()}
    </div>
  );
}
