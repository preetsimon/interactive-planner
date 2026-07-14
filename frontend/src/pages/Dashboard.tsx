import { useEffect, useState, useMemo } from 'react';
import {
  Clock, Target, TrendingUp, AlertTriangle, Scissors,
  CheckCircle, ArrowRight, Shield, Calendar,
} from 'lucide-react';
import { StatCard } from '@/components/ui/StatCard';
import { WeeklyHoursChart } from '@/components/charts/WeeklyHoursChart';
import { CategoryDonut } from '@/components/charts/CategoryDonut';
import { SprintRing } from '@/components/charts/SprintRing';
import { QuarterTimeline } from '@/components/charts/QuarterTimeline';
import { ActivityHeatmap } from '@/components/charts/ActivityHeatmap';
import {
  prioritiesApi, cadenceApi, auditLogApi, timeBlocksApi, learningApi,
} from '@/services/api';
import type { Priority, Quarter, AuditLogEntry, TimeBlock } from '@/services/types';

const DAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const CATEGORY_COLORS: Record<string, string> = {
  CODING_PROACTIVE: '#6366f1',
  FRENCH_OUTPUT: '#f59e0b',
  JOB: '#64748b',
  CODING_REACTIVE: '#f97316',
  FRENCH_PASSIVE: '#fbbf24',
  JOB_SEARCH_NOISE: '#94a3b8',
  PASSIVE_CONSUMPTION: '#cbd5e1',
  REST: '#22c55e',
  LIFE: '#8b5cf6',
};

function getWeekRange(): { from: string; to: string } {
  const now = new Date();
  const monday = new Date(now);
  monday.setDate(now.getDate() - ((now.getDay() + 6) % 7));
  monday.setHours(0, 0, 0, 0);
  const sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);
  sunday.setHours(23, 59, 59, 999);
  return {
    from: monday.toISOString(),
    to: sunday.toISOString(),
  };
}

function groupBlocksByDay(blocks: TimeBlock[]) {
  const result = DAY_LABELS.map((day) => ({
    day,
    hours: 0,
    proactive: 0,
    reactive: 0,
  }));

  for (const block of blocks) {
    const d = new Date(block.start_at);
    const dayIdx = (d.getDay() + 6) % 7;
    const hours = (new Date(block.end_at).getTime() - d.getTime()) / 3600000;
    result[dayIdx].hours += hours;
    if (block.category_id) {
      result[dayIdx].proactive += hours * 0.6;
      result[dayIdx].reactive += hours * 0.4;
    }
  }

  return result;
}

function groupBlocksByCategory(blocks: TimeBlock[]) {
  const map = new Map<string, number>();
  for (const block of blocks) {
    const hours = (new Date(block.end_at).getTime() - new Date(block.start_at).getTime()) / 3600000;
    const key = block.category_id;
    map.set(key, (map.get(key) || 0) + hours);
  }
  return Array.from(map.entries())
    .map(([id, hours]) => ({
      label: id.slice(0, 8),
      hours,
      color: CATEGORY_COLORS[id] || '#64748b',
    }))
    .sort((a, b) => b.hours - a.hours)
    .slice(0, 6);
}

const CARD = 'rounded-xl border border-gray-100 bg-white p-5 shadow-card transition-shadow hover:shadow-card-hover dark:border-gray-800/60 dark:bg-gray-900/50';

export function Dashboard() {
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [quarter, setQuarter] = useState<Quarter | null>(null);
  const [violations, setViolations] = useState<AuditLogEntry[]>([]);
  const [timeBlocks, setTimeBlocks] = useState<TimeBlock[]>([]);
  const [activityData, setActivityData] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const { from, to } = getWeekRange();
    Promise.all([
      prioritiesApi.list('ACTIVE').catch(() => []),
      cadenceApi.current().catch(() => null),
      auditLogApi.list().catch(() => []),
      timeBlocksApi.list(from, to).catch(() => []),
      learningApi.activity().catch(() => ({})),
    ]).then(([p, q, v, tb, activity]) => {
      setPriorities(p);
      setQuarter(q);
      setViolations(
        v.filter((e) => e.event_type.includes('VIOLATION') || e.event_type.includes('UNUSED'))
      );
      setTimeBlocks(tb);
      setActivityData(activity);
      setLoading(false);
    });
  }, []);

  const weekData = useMemo(() => groupBlocksByDay(timeBlocks), [timeBlocks]);
  const categoryData = useMemo(() => groupBlocksByCategory(timeBlocks), [timeBlocks]);
  const totalWeekHours = weekData.reduce((s, d) => s + d.hours, 0);

  const techCount = priorities.filter((p) => p.track === 'TECHNICAL').length;
  const langCount = priorities.filter((p) => p.track === 'LANGUAGE').length;

  const weekNum = quarter?.sprint_start
    ? Math.min(8, Math.max(1, Math.ceil(
        (Date.now() - new Date(quarter.sprint_start).getTime()) / (7 * 86400000)
      ) + 1))
    : 0;

  const daysLeft = quarter?.sprint_end
    ? Math.max(0, Math.ceil(
        (new Date(quarter.sprint_end).getTime() - Date.now()) / 86400000
      ))
    : null;

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-900 border-t-transparent dark:border-gray-100 dark:border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">Dashboard</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {quarter
              ? `Q${quarter.quarter_num} ${quarter.year} — ${quarter.phase}`
              : 'No active quarter'}
          </p>
        </div>
        {quarter && (
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Calendar size={14} />
            {quarter.sprint_start && quarter.sprint_end && (
              <span>
                {new Date(quarter.sprint_start).toLocaleDateString()} — {new Date(quarter.sprint_end).toLocaleDateString()}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Hours This Week"
          value={`${totalWeekHours.toFixed(1)}h`}
          icon={Clock}
          sparkline={weekData.map((d) => d.hours)}
        />
        <StatCard
          title="Active Priorities"
          value={priorities.length}
          subtitle={`${techCount} tech · ${langCount} lang`}
          icon={Target}
        />
        <StatCard
          title="Sprint Progress"
          value={weekNum ? `${weekNum}/8` : '—'}
          subtitle={daysLeft !== null ? `${daysLeft} days left` : undefined}
          progress={weekNum ? (weekNum / 8) * 100 : 0}
          icon={TrendingUp}
        />
        <StatCard
          title="Violations"
          value={violations.length}
          change={violations.length > 0 ? 'Needs attention' : 'All clear'}
          changeType={violations.length > 0 ? 'negative' : 'positive'}
          icon={AlertTriangle}
        />
      </div>

      {/* Activity heatmap */}
      <div className={CARD}>
        <ActivityHeatmap data={activityData} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div className={CARD}>
            <WeeklyHoursChart data={weekData} />
          </div>

          <div className={CARD}>
            {categoryData.length === 0 ? (
              <div className="text-center py-8">
                <Clock size={32} className="mx-auto text-gray-300 dark:text-gray-700 mb-2" />
                <p className="text-sm text-gray-400">No time blocks this week</p>
                <p className="text-xs text-gray-400 mt-1">Start logging time to see breakdown</p>
              </div>
            ) : (
              <CategoryDonut segments={categoryData} centerLabel="hours" />
            )}
          </div>
        </div>

        <div className="space-y-6">
          {quarter && (
            <div className={CARD}>
              <SprintRing
                currentWeek={weekNum || 0}
                totalWeeks={8}
                phase={quarter.phase}
              />
            </div>
          )}

          <div className={CARD}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-[13px] font-medium text-gray-700 dark:text-gray-300">
                Active Priorities
              </h3>
              <a href="/priorities" className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                View all
              </a>
            </div>
            {priorities.length === 0 ? (
              <p className="text-sm text-gray-400 py-4 text-center">No active priorities</p>
            ) : (
              <div className="space-y-3">
                {priorities.map((p) => (
                  <div
                    key={p.id}
                    className="rounded-lg border border-gray-100 p-3 dark:border-gray-800/60"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          {p.title}
                        </p>
                        <p className="text-[10px] text-gray-400 mt-0.5 truncate">
                          {p.definition_of_done}
                        </p>
                      </div>
                      <span
                        className={`ml-2 flex-shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold ${
                          p.track === 'TECHNICAL'
                            ? 'bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400'
                            : 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400'
                        }`}
                      >
                        {p.track}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {quarter && (
        <div className={CARD}>
          <QuarterTimeline
            phase={quarter.phase}
            sprintStart={quarter.sprint_start}
            sprintEnd={quarter.sprint_end}
          />
        </div>
      )}

      {violations.length > 0 && (
        <div className={CARD}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[13px] font-medium text-gray-700 dark:text-gray-300">
              Recent Violations
            </h3>
            <a href="/audit-log" className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              Full log
            </a>
          </div>
          <div className="space-y-2">
            {violations.slice(0, 4).map((v) => (
              <div
                key={v.id}
                className="flex items-center gap-3 rounded-lg bg-red-50/50 p-3 dark:bg-red-500/5"
              >
                <Shield size={14} className="text-red-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-gray-900 dark:text-gray-100">
                    {v.event_type.replace(/_/g, ' ')}
                  </p>
                  <p className="text-[10px] text-gray-500 dark:text-gray-400 truncate">
                    {v.detail ? JSON.stringify(v.detail) : v.entity_type}
                  </p>
                </div>
                <span className="text-[10px] text-gray-400 flex-shrink-0">
                  {new Date(v.occurred_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
