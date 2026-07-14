import { Moon, Sun, LogOut } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';

interface HeaderProps {
  sidebarWidth: string;
}

export function Header({ sidebarWidth }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  return (
    <header
      className="fixed right-0 top-0 z-30 flex h-14 items-center justify-between border-b border-gray-100 bg-white/80 px-6 backdrop-blur-sm transition-all duration-300 dark:bg-gray-950/80 dark:border-gray-800/60"
      style={{ left: sidebarWidth }}
    >
      <div>
        <span className="text-[13px] font-medium text-gray-500 dark:text-gray-400">
          {user?.email || 'Welcome back'}
        </span>
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-gray-400 hover:bg-gray-50 hover:text-gray-600 dark:text-gray-500 dark:hover:bg-gray-800/50 dark:hover:text-gray-300"
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        <button
          onClick={logout}
          className="rounded-lg p-2 text-gray-400 hover:bg-gray-50 hover:text-gray-600 dark:text-gray-500 dark:hover:bg-gray-800/50 dark:hover:text-gray-300"
          title="Sign out"
        >
          <LogOut size={16} />
        </button>

        <div className="ml-1 flex h-7 w-7 items-center justify-center rounded-full bg-gray-900 text-[11px] font-semibold text-white dark:bg-gray-100 dark:text-gray-900">
          {user?.email?.[0]?.toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  );
}
