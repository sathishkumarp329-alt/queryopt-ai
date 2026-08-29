import { useEffect, useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  Database,
  LayoutDashboard,
  Zap,
  BarChart3,
  Clock,
  Circle,
} from 'lucide-react';
import { getHealth } from '../services/api';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyzer', label: 'SQL Analyzer', icon: Zap },
  { to: '/evaluation', label: 'Evaluation', icon: BarChart3 },
  { to: '/history', label: 'History', icon: Clock },
];

export default function Layout() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        await getHealth();
        if (!cancelled) setApiStatus('online');
      } catch {
        if (!cancelled) setApiStatus('offline');
      }
    };
    check();
    const interval = setInterval(check, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      {/* Sidebar */}
      <aside className="flex flex-col w-64 shrink-0 bg-gray-900 border-r border-gray-800">
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-800">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-emerald-500/20 border border-emerald-500/30">
            <Database className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-100 leading-none">QueryOpt AI</p>
            <p className="text-xs text-gray-500 mt-0.5">SQL Analysis</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-400 border-r-2 border-emerald-400'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer: API status */}
        <div className="px-4 py-4 border-t border-gray-800">
          <div className="flex items-center gap-2">
            <Circle
              className={`w-2.5 h-2.5 fill-current ${
                apiStatus === 'online'
                  ? 'text-emerald-400'
                  : apiStatus === 'offline'
                  ? 'text-red-400'
                  : 'text-yellow-400 animate-pulse'
              }`}
            />
            <span className="text-xs text-gray-500">
              API{' '}
              {apiStatus === 'online'
                ? 'Online'
                : apiStatus === 'offline'
                ? 'Offline'
                : 'Checking…'}
            </span>
            {apiStatus === 'offline' && (
              <span className="ml-auto text-xs text-red-400">
                localhost:8000
              </span>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
