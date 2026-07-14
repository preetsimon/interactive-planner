import { useCallback, useEffect, useState } from 'react';
import { GraduationCap, Flame, CheckCircle2, Circle, Moon, Sparkles } from 'lucide-react';
import { learningApi } from '@/services/api';
import type { LearningTrack, LearningTrackDetail, CurriculumItem } from '@/services/types';

function ProgressBar({ done, total }: { done: number; total: number }) {
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
        <div
          className="h-full rounded-full bg-indigo-600 transition-all dark:bg-indigo-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
        {done}/{total}
      </span>
    </div>
  );
}

export function Learning() {
  const [tracks, setTracks] = useState<LearningTrack[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<LearningTrackDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadTracks = useCallback(async () => {
    try {
      const list = await learningApi.listTracks();
      setTracks(list);
      setSelectedId((prev) => prev ?? list[0]?.id ?? null);
    } catch {
      setError('Failed to load learning tracks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadTracks(); }, [loadTracks]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    let cancelled = false;
    learningApi.getTrack(selectedId)
      .then((d) => { if (!cancelled) setDetail(d); })
      .catch(() => { if (!cancelled) setError('Failed to load track detail'); });
    return () => { cancelled = true; };
  }, [selectedId]);

  const refreshDetail = async () => {
    if (!selectedId) return;
    try {
      setDetail(await learningApi.getTrack(selectedId));
      setTracks(await learningApi.listTracks());
    } catch {
      setError('Failed to refresh track');
    }
  };

  const handleSeed = async () => {
    setError('');
    try {
      const list = await learningApi.seedDefaults();
      setTracks(list);
      setSelectedId(list[0]?.id ?? null);
    } catch {
      setError('Failed to set up curricula');
    }
  };

  const handleToggleItem = async (item: CurriculumItem) => {
    setError('');
    try {
      await learningApi.toggleItem(item.id);
      await refreshDetail();
    } catch {
      setError('Failed to update item');
    }
  };

  const handleToggleRoutine = async (routineId: string, todayDone: boolean) => {
    setError('');
    try {
      if (todayDone) {
        await learningApi.unlogPractice(routineId);
      } else {
        await learningApi.logPractice(routineId);
      }
      await refreshDetail();
    } catch {
      setError('Failed to update practice log');
    }
  };

  const sections: { name: string; items: CurriculumItem[] }[] = [];
  if (detail) {
    for (const item of detail.items) {
      const last = sections[sections.length - 1];
      if (last && last.name === item.section) {
        last.items.push(item);
      } else {
        sections.push({ name: item.section, items: [item] });
      }
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">Learning</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Curricula, daily practice, and streaks
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center text-sm text-gray-400">Loading...</div>
      ) : tracks.length === 0 ? (
        <div className="rounded-xl border border-gray-100 bg-white p-10 text-center shadow-card dark:border-gray-800/60 dark:bg-gray-900/50">
          <GraduationCap size={32} className="mx-auto text-indigo-600 dark:text-indigo-400" />
          <h3 className="mt-3 text-sm font-semibold text-gray-900 dark:text-gray-100">
            No learning tracks yet
          </h3>
          <p className="mx-auto mt-1 max-w-md text-xs text-gray-500 dark:text-gray-400">
            Load your two curricula: the Python bootcamp (JS → Python, four resources +
            assay-qc-service) and the French A1 → CLB 7 roadmap (cartoons + grammar + Anki).
          </p>
          <button
            onClick={handleSeed}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            <Sparkles size={16} />
            Set up my curricula
          </button>
        </div>
      ) : (
        <>
          {/* Track tabs */}
          <div className="flex flex-wrap gap-2">
            {tracks.map((t) => (
              <button
                key={t.id}
                onClick={() => setSelectedId(t.id)}
                className={`rounded-lg border px-4 py-2 text-sm font-medium transition-all duration-200 ${
                  t.id === selectedId
                    ? 'border-indigo-600 bg-indigo-50 text-indigo-700 dark:border-indigo-500 dark:bg-indigo-500/10 dark:text-indigo-400'
                    : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-400 dark:hover:bg-gray-800'
                }`}
              >
                {t.name}
                <span className="ml-2 text-xs opacity-70">
                  {t.items_done}/{t.items_total}
                </span>
              </button>
            ))}
          </div>

          {detail && (
            <>
              <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-card dark:border-gray-800/60 dark:bg-gray-900/50">
                <p className="text-xs leading-relaxed text-gray-500 dark:text-gray-400">
                  {detail.description}
                </p>
                <div className="mt-4">
                  <ProgressBar done={detail.items_done} total={detail.items_total} />
                </div>
              </div>

              {/* Today's practice */}
              {detail.routines.length > 0 && (
                <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-card dark:border-gray-800/60 dark:bg-gray-900/50">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    Today's practice
                  </h3>
                  <div className="mt-3 space-y-2">
                    {detail.routines.map((r) => (
                      <div
                        key={r.id}
                        className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
                      >
                        <button
                          onClick={() => handleToggleRoutine(r.id, r.today_done)}
                          className="flex items-center gap-3 text-left"
                        >
                          {r.today_done ? (
                            <CheckCircle2 size={20} className="shrink-0 text-emerald-600 dark:text-emerald-400" />
                          ) : (
                            <Circle size={20} className="shrink-0 text-gray-300 dark:text-gray-600" />
                          )}
                          <span
                            className={`text-sm ${
                              r.today_done
                                ? 'text-gray-400 line-through dark:text-gray-500'
                                : 'text-gray-800 dark:text-gray-200'
                            }`}
                          >
                            {r.name}
                          </span>
                          {r.minutes != null && (
                            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                              {r.minutes} min
                            </span>
                          )}
                          {r.is_rest_today && (
                            <span className="flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-600 dark:bg-blue-500/10 dark:text-blue-400">
                              <Moon size={12} />
                              Rest day
                            </span>
                          )}
                        </button>
                        <span
                          className={`flex items-center gap-1 text-sm font-semibold ${
                            r.streak > 0
                              ? 'text-orange-500'
                              : 'text-gray-300 dark:text-gray-600'
                          }`}
                        >
                          <Flame size={16} />
                          {r.streak}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Curriculum */}
              {sections.map((section) => {
                const done = section.items.filter((i) => i.status === 'DONE').length;
                return (
                  <div
                    key={section.name}
                    className="rounded-xl border border-gray-100 bg-white p-5 shadow-card dark:border-gray-800/60 dark:bg-gray-900/50"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                        {section.name}
                      </h3>
                      <div className="w-40">
                        <ProgressBar done={done} total={section.items.length} />
                      </div>
                    </div>
                    <div className="mt-3 space-y-1">
                      {section.items.map((item) => (
                        <button
                          key={item.id}
                          onClick={() => handleToggleItem(item)}
                          className="flex w-full items-start gap-3 rounded-lg px-2 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50"
                        >
                          {item.status === 'DONE' ? (
                            <CheckCircle2 size={18} className="mt-0.5 shrink-0 text-emerald-600 dark:text-emerald-400" />
                          ) : (
                            <Circle size={18} className="mt-0.5 shrink-0 text-gray-300 dark:text-gray-600" />
                          )}
                          <span>
                            <span
                              className={`block text-sm ${
                                item.status === 'DONE'
                                  ? 'text-gray-400 line-through dark:text-gray-500'
                                  : 'text-gray-800 dark:text-gray-200'
                              }`}
                            >
                              {item.title}
                            </span>
                            {item.details && (
                              <span className="mt-0.5 block text-xs leading-relaxed text-gray-500 dark:text-gray-400">
                                {item.details}
                              </span>
                            )}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                );
              })}
            </>
          )}
        </>
      )}
    </div>
  );
}
