import { useEffect, useState } from 'react';
import { Shield } from 'lucide-react';
import { auditLogApi } from '@/services/api';
import type { AuditLogEntry } from '@/services/types';

const eventColors: Record<string, string> = {
  PROTECTED_WINDOW_VIOLATION: 'bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400',
  CUTOFF_VIOLATION: 'bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400',
  PROTECTED_WINDOW_UNUSED: 'bg-orange-100 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400',
  PRIORITY_REJECTED: 'bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400',
  PRIORITY_CUT: 'bg-gray-100 text-gray-700 dark:bg-gray-500/10 dark:text-gray-400',
  FORCED_SHIP: 'bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400',
  DOMAIN_CUT: 'bg-gray-100 text-gray-700 dark:bg-gray-500/10 dark:text-gray-400',
};

export function AuditLog() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    auditLogApi.list().then(setEntries).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Audit Log</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Append-only event stream — nothing gets silently ignored
        </p>
      </div>

      <div className="rounded-xl border bg-white shadow-sm dark:bg-gray-900 dark:border-gray-800">
        {loading ? (
          <div className="p-8 text-center text-sm text-gray-400">Loading...</div>
        ) : entries.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-400">
            No audit events yet.
          </div>
        ) : (
          <div className="divide-y divide-gray-100 dark:divide-gray-800">
            {entries.map((entry) => (
              <div key={entry.id} className="flex items-start gap-4 p-4">
                <div className="mt-0.5 rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
                  <Shield size={14} className="text-gray-400" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                        eventColors[entry.event_type] || 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                      }`}
                    >
                      {entry.event_type}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(entry.occurred_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    {entry.entity_type}
                    {entry.detail && (
                      <span className="ml-2 text-xs text-gray-400">
                        {JSON.stringify(entry.detail)}
                      </span>
                    )}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
