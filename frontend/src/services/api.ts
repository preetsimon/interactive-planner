import type {
  TimeBlock, Priority, Quarter, Domain, AuditReport, AuditLogEntry,
  LearningTrack, LearningTrackDetail, CurriculumItem,
} from './types';

const API_BASE = '/api/v1';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('pos-token', token);
    } else {
      localStorage.removeItem('pos-token');
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('pos-token');
    }
    return this.token;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401 && !path.startsWith('/auth/')) {
      this.setToken(null);
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw { status: res.status, ...error };
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  }

  get<T>(path: string) {
    return this.request<T>('GET', path);
  }

  post<T>(path: string, body?: unknown) {
    return this.request<T>('POST', path, body);
  }

  put<T>(path: string, body?: unknown) {
    return this.request<T>('PUT', path, body);
  }

  delete<T>(path: string) {
    return this.request<T>('DELETE', path);
  }
}

export const api = new ApiClient();

// ---- Auth ----
export const authApi = {
  register: (data: { email: string; password: string; stated_goal?: string }) =>
    api.post<{ id: string; email: string }>('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string }>('/auth/login', data),
};

// ---- Time Blocks ----
export const timeBlocksApi = {
  list: (from?: string, to?: string) => {
    const params = new URLSearchParams();
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    const qs = params.toString();
    return api.get<TimeBlock[]>(`/time-blocks${qs ? `?${qs}` : ''}`);
  },
  create: (data: { category_id: string; start_at: string; end_at: string; notes?: string }) =>
    api.post<TimeBlock>('/time-blocks', data),
  remove: (id: string) => api.delete(`/time-blocks/${id}`),
};

// ---- Priorities ----
export const prioritiesApi = {
  list: (status?: string) => {
    const qs = status ? `?status=${status}` : '';
    return api.get<Priority[]>(`/priorities${qs}`);
  },
  create: (data: { title: string; track: string; definition_of_done: string }) =>
    api.post<Priority>('/priorities', data),
  cut: (id: string) => api.post<Priority>(`/priorities/${id}/cut`),
  complete: (id: string) => api.post<Priority>(`/priorities/${id}/complete`),
};

// ---- Cadence ----
export const cadenceApi = {
  current: () => api.get<Quarter | null>('/cadence/current'),
  createQuarter: (data: { year: number; quarter_num: number; theme?: string }) =>
    api.post<Quarter>('/cadence/quarters', data),
  tick: () => api.post<Quarter>('/cadence/tick'),
};

// ---- Domains ----
export const domainsApi = {
  list: () => api.get<Domain[]>('/domains'),
  create: (data: { name: string; required_assets?: string[] }) =>
    api.post<Domain>('/domains', data),
  rescore: () => api.post<Domain[]>('/domains/rescore'),
};

// ---- Reports & Audit Log ----
export const reportsApi = {
  list: (type?: string, from?: string, to?: string) => {
    const params = new URLSearchParams();
    if (type) params.set('type', type);
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    const qs = params.toString();
    return api.get<AuditReport[]>(`/reports${qs ? `?${qs}` : ''}`);
  },
};

// ---- Learning ----
export const learningApi = {
  listTracks: () => api.get<LearningTrack[]>('/learning/tracks'),
  seedDefaults: () => api.post<LearningTrack[]>('/learning/seed-defaults'),
  getTrack: (id: string) => api.get<LearningTrackDetail>(`/learning/tracks/${id}`),
  toggleItem: (itemId: string) =>
    api.post<CurriculumItem>(`/learning/items/${itemId}/toggle`),
  logPractice: (routineId: string, data?: { log_date?: string; minutes?: number }) =>
    api.post(`/learning/routines/${routineId}/log`, data ?? {}),
  unlogPractice: (routineId: string) =>
    api.delete(`/learning/routines/${routineId}/log`),
};

export const auditLogApi = {
  list: (from?: string, to?: string) => {
    const params = new URLSearchParams();
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    const qs = params.toString();
    return api.get<AuditLogEntry[]>(`/audit-log${qs ? `?${qs}` : ''}`);
  },
};
