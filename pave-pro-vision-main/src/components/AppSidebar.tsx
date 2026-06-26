import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Route, PlusCircle, Cpu, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/roads', label: 'Road Segments', icon: Route },
  { to: '/add-road', label: 'Add Road', icon: PlusCircle },
  { to: '/digital-twins', label: 'Digital Twins', icon: Cpu },
];

export function AppSidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-sidebar border-r border-sidebar-border flex flex-col z-50">
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <Activity className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-foreground tracking-wide">RoadTwin</h1>
            <p className="text-[10px] text-muted-foreground font-mono uppercase tracking-widest">Digital Twin System</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {links.map(({ to, label, icon: Icon }) => {
          const isActive = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to);
          return (
            <NavLink
              key={to}
              to={to}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-all',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-sidebar-border">
        <div className="bg-muted rounded-md p-3">
          <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest mb-1">System Status</p>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-risk-low animate-pulse-glow" />
            <span className="text-xs text-foreground">All systems operational</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
