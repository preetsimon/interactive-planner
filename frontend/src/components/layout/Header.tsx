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
      className={`fixed right-0 top-0 z-30 flex h-16 items-center justify-between border-b bg-white/80 px-6 backdrop-blur-sm transition-all duration-300 dark:bg-gray-900/80 dark:border-gray-800`}
      style={{ left: sidebarWidth }}
    >
      <div>
        <h1 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          {user?.email || 'Welcome back'}
        </h1>
      </div>

      <div className="flex items-center gap-2">
        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* Logout */}
        <button
          onClick={logout}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          title="Sign out"
        >
          <LogOut size={18} />
        </button>

        {/* Avatar */}
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
          {user?.email?.[0]?.toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  );
}
