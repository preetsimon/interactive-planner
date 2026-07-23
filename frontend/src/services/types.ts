export interface TimeBlock {
  id: string;
  category_id: string;
  start_at: string;
  end_at: string;
  notes: string | null;
  violates_protected_window: boolean;
  violates_cutoff: boolean;
}

export interface Priority {
  id: string;
  title: string;
  track: 'TECHNICAL' | 'LANGUAGE';
  status: 'ACTIVE' | 'COMPLETED' | 'CUT' | 'REJECTED';
  definition_of_done: string;
}

export interface Quarter {
  id: string;
  year: number;
  quarter_num: number;
  theme: string;
  phase: 'REST' | 'REVIEW' | 'SPRINT' | 'CLOSED';
  sprint_start: string | null;
  sprint_end: string | null;
}

export interface Domain {
  id: string;
  name: string;
  score: number;
  status: 'ACTIVE' | 'CUT';
  required_assets: string[] | null;
}

export interface AuditReport {
  id: string;
  type: string;
  period_start: string;
  period_end: string;
  verdict: string;
  payload: Record<string, unknown> | null;
}

export interface LearningTrack {
  id: string;
  slug: string;
  name: string;
  description: string;
  items_total: number;
  items_done: number;
}

export interface CurriculumItem {
  id: string;
  section: string;
  title: string;
  details: string | null;
  learning_goal: string | null;
  key_topics: string[] | null;
  sort_order: number;
  status: 'PENDING' | 'DONE';
  completed_at: string | null;
}

export interface PracticeRoutine {
  id: string;
  name: string;
  minutes: number | null;
  rest_weekdays: number[];
  is_rest_today: boolean;
  today_done: boolean;
  today_minutes: number | null;
  streak: number;
}

export interface LearningTrackDetail extends LearningTrack {
  items: CurriculumItem[];
  routines: PracticeRoutine[];
}

export interface AuditLogEntry {
  id: string;
  event_type: string;
  entity_type: string;
  entity_id: string | null;
  detail: Record<string, unknown> | null;
  occurred_at: string;
}
