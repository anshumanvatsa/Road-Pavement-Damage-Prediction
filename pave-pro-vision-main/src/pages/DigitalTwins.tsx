import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Cpu, Search } from 'lucide-react';
import { useAllRoads } from '@/lib/store';
import { createDigitalTwin } from '@/lib/digital-twin';
import { RiskBadge } from '@/components/RiskBadge';
import { Input } from '@/components/ui/input';
import type { RiskLevel } from '@/lib/types';

export default function DigitalTwins() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [filterRisk, setFilterRisk] = useState<RiskLevel | 'All'>('All');

  const { data: roads, loading } = useAllRoads();
  
  const twinsData = useMemo(() => {
    if (!roads) return [];
    return roads.map(road => ({ road, twin: createDigitalTwin(road) }));
  }, [roads]);

  const filtered = useMemo(() => {
    let result = twinsData;
    if (filterRisk !== 'All') result = result.filter(d => d.twin.risk_level === filterRisk);
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(d => d.road.road_name.toLowerCase().includes(q) || d.road.location.toLowerCase().includes(q));
    }
    return result;
  }, [twinsData, search, filterRisk]);

  if (loading) return <div className="p-8">Loading digital twins...</div>;

  const riskFilters: (RiskLevel | 'All')[] = ['All', 'High', 'Medium', 'Low'];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Digital Twins</h1>
        <p className="text-sm text-muted-foreground mt-1">Virtual representations of all road segments</p>
      </div>

      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search twins..." value={search} onChange={e => setSearch(e.target.value)} className="pl-9 bg-card border-border" />
        </div>
        <div className="flex gap-1 bg-card border border-border rounded-md p-1">
          {riskFilters.map(r => (
            <button
              key={r}
              onClick={() => setFilterRisk(r)}
              className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${filterRisk === r ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(({ road, twin }, i) => (
          <motion.div
            key={road.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.02 }}
            onClick={() => navigate(`/roads/${road.id}`)}
            className="bg-card border border-border rounded-lg p-5 hover:border-primary/30 transition-colors cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded bg-primary/15 flex items-center justify-center">
                  <Cpu className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">{road.road_name}</p>
                  <p className="text-xs text-muted-foreground">{road.location}</p>
                </div>
              </div>
              <RiskBadge level={twin.risk_level} />
            </div>

            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                  <span>Current</span>
                  <span className="font-mono">{twin.current_state}</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${twin.current_state}%` }} />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                  <span>Predicted</span>
                  <span className="font-mono">{twin.predicted_state}</span>
                </div>
                <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-risk-medium transition-all" style={{ width: `${twin.predicted_state}%` }} />
                </div>
              </div>
            </div>

            <p className="text-xs text-muted-foreground mt-3 pt-3 border-t border-border">{twin.maintenance_recommendation}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
