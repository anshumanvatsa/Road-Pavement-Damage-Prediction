import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Route, AlertTriangle, Shield, Activity, TrendingDown } from 'lucide-react';
import { useDashboardStats, useAllRoads, useAllDigitalTwins } from '@/lib/store';
import { StatCard } from '@/components/StatCard';
import { RiskBadge } from '@/components/RiskBadge';
import { PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const RISK_COLORS = {
  Low: 'hsl(145, 65%, 42%)',
  Medium: 'hsl(38, 92%, 55%)',
  High: 'hsl(0, 72%, 55%)',
};

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: stats, loading: statsLoading } = useDashboardStats();
  const { data: roads } = useAllRoads();
  const twins = useAllDigitalTwins();

  // If loading, show simple fallback
  if (statsLoading) return <div className="p-8">Loading dashboard...</div>;

  const pieData = [
    { name: 'Low', value: stats.low },
    { name: 'Medium', value: stats.medium },
    { name: 'High', value: stats.high },
  ];

  const conditionDistribution = useMemo(() => {
    const buckets = Array.from({ length: 10 }, (_, i) => ({
      range: `${i * 10}-${(i + 1) * 10}`,
      count: 0,
    }));
    roads.forEach(r => {
      const idx = Math.min(Math.floor(r.current_condition_index / 10), 9);
      buckets[idx].count++;
    });
    return buckets;
  }, [roads]);

  const highRiskRoads = useMemo(() =>
    twins.filter(t => t.risk_level === 'High').slice(0, 5).map(t => {
      const road = roads.find(r => r.id === t.road_segment_id);
      return road ? { ...t, road } : null;
    }).filter(Boolean) as any[], [twins, roads]);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Climate-aware road degradation monitoring</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard title="Total Roads" value={stats.total} icon={Route} variant="primary" subtitle="Monitored segments" />
        <StatCard title="High Risk" value={stats.high} icon={AlertTriangle} variant="risk-high" subtitle="Immediate attention" />
        <StatCard title="Medium Risk" value={stats.medium} icon={TrendingDown} variant="risk-medium" subtitle="Schedule maintenance" />
        <StatCard title="Low Risk" value={stats.low} icon={Shield} variant="risk-low" subtitle="Normal monitoring" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="bg-card border border-border rounded-lg p-5 lg:col-span-2">
          <h3 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">Condition Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={conditionDistribution}>
              <XAxis dataKey="range" stroke="hsl(215, 15%, 55%)" fontSize={11} tickLine={false} />
              <YAxis stroke="hsl(215, 15%, 55%)" fontSize={11} tickLine={false} />
              <Tooltip contentStyle={{ background: 'hsl(220, 22%, 10%)', border: '1px solid hsl(220, 18%, 18%)', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="count" fill="hsl(185, 65%, 48%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="bg-card border border-border rounded-lg p-5">
          <h3 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={4} dataKey="value" stroke="none">
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={RISK_COLORS[entry.name as keyof typeof RISK_COLORS]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: 'hsl(220, 22%, 10%)', border: '1px solid hsl(220, 18%, 18%)', borderRadius: 8, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {pieData.map(d => (
              <div key={d.name} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: RISK_COLORS[d.name as keyof typeof RISK_COLORS] }} />
                {d.name} ({d.value})
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="bg-card border border-border rounded-lg p-5">
        <h3 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">Critical Roads — Highest Risk</h3>
        <div className="space-y-3">
          {highRiskRoads.map(({ road, risk_level, predicted_state, maintenance_recommendation }) => (
            <div
              key={road.id}
              onClick={() => navigate(`/roads/${road.id}`)}
              className="flex items-center justify-between p-3 bg-muted/50 rounded-md border border-border hover:border-risk-high/30 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded bg-risk-high/15 flex items-center justify-center">
                  <AlertTriangle className="w-4 h-4 text-risk-high" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">{road.road_name}</p>
                  <p className="text-xs text-muted-foreground">{road.location}</p>
                </div>
              </div>
              <div className="text-right flex items-center gap-4">
                <div>
                  <p className="text-xs text-muted-foreground">Predicted</p>
                  <p className="text-sm font-mono text-foreground">{predicted_state}</p>
                </div>
                <RiskBadge level={risk_level} />
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
