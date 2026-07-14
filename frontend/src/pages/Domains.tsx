import { useEffect, useState } from 'react';
import { Globe, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { domainsApi } from '@/services/api';
import type { Domain } from '@/services/types';

export function Domains() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    domainsApi.list().then(setDomains).finally(() => setLoading(false));
  }, []);

  const handleRescore = async () => {
    const rescored = await domainsApi.rescore();
    setDomains(rescored);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">Target Domains</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Niche filter — scored by asset overlap
          </p>
        </div>
        {domains.length > 0 && (
          <button
            onClick={handleRescore}
            className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            <RefreshCw size={14} />
            Rescore
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center text-sm text-gray-400">Loading...</div>
      ) : domains.length === 0 ? (
        <div className="text-center text-sm text-gray-400">
          No target domains yet. Add domains to enable niche filtering.
        </div>
      ) : (
        <div className="space-y-3">
          {domains.map((domain) => (
            <div
              key={domain.id}
              className={`rounded-xl border border-gray-100 bg-white p-5 shadow-card transition-shadow hover:shadow-card-hover dark:border-gray-800/60 dark:bg-gray-900/50 ${
                domain.status === 'CUT' ? 'opacity-60' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Globe size={16} className="text-indigo-600 dark:text-indigo-400" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {domain.name}
                    </p>
                    {domain.required_assets && domain.required_assets.length > 0 && (
                      <div className="mt-1 flex gap-1">
                        {domain.required_assets.map((a) => (
                          <span
                            key={a}
                            className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                          >
                            {a}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {Math.round(domain.score * 100)}%
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">match</p>
                  </div>
                  {domain.status === 'ACTIVE' ? (
                    <TrendingUp size={16} className="text-emerald-500" />
                  ) : (
                    <TrendingDown size={16} className="text-red-500" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
