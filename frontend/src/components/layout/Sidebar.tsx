import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Clock,
  Target,
  Calendar,
  BarChart3,
  Globe,
  Shield,
  GraduationCap,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/time-blocks', icon: Clock, label: 'Time Blocks' },
  { to: '/priorities', icon: Target, label: 'Priorities' },
  { to: '/cadence', icon: Calendar, label: 'Cadence' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/domains', icon: Globe, label: 'Domains' },
  { to: '/learning', icon: GraduationCap, label: 'Learning' },
  { to: '/audit-log', icon: Shield, label: 'Audit Log' },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={`fixed left-0 top-0 z-40 h-screen border-r transition-all duration-300
        ${collapsed ? 'w-16' : 'w-64'}
        bg-white/80 backdrop-blur-sm border-gray-100
        dark:bg-gray-950/90 dark:border-gray-800/60`}
    >
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center justify-between border-b border-gray-100 px-4 dark:border-gray-800/60">
          {!collapsed && (
            <span className="text-base font-semibold tracking-tight text-gray-900 dark:text-gray-100">
              POS
            </span>
          )}
          <button
            onClick={onToggle}
            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-50 hover:text-gray-600 dark:text-gray-500 dark:hover:bg-gray-800/50 dark:hover:text-gray-300"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        <nav className="flex-1 space-y-0.5 px-3 py-4">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-[13px] font-medium transition-colors
                ${
                  isActive
                    ? 'bg-gray-100 text-gray-900 dark:bg-gray-800/60 dark:text-gray-100'
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800/40 dark:hover:text-gray-300'
                }
                ${collapsed ? 'justify-center' : ''}`
              }
            >
              <Icon size={18} strokeWidth={1.75} />
              {!collapsed && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {!collapsed && (
          <div className="border-t border-gray-100 px-4 py-3 dark:border-gray-800/60">
            <p className="text-[11px] text-gray-400 dark:text-gray-600">
              Personal Operating System
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
