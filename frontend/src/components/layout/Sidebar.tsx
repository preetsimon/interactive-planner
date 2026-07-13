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
        bg-white border-gray-200
        dark:bg-gray-900 dark:border-gray-800`}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b px-4 dark:border-gray-800">
          {!collapsed && (
            <span className="text-lg font-bold tracking-tight text-indigo-600 dark:text-indigo-400">
              POS
            </span>
          )}
          <button
            onClick={onToggle}
            className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          >
            {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-2 py-4">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors
                ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200'
                }
                ${collapsed ? 'justify-center' : ''}`
              }
            >
              <Icon size={20} />
              {!collapsed && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        {!collapsed && (
          <div className="border-t px-4 py-3 dark:border-gray-800">
            <p className="text-xs text-gray-400 dark:text-gray-500">
              Personal Operating System
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
