import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search } from 'lucide-react';
import { useAllRoads } from '@/lib/store';
import { createDigitalTwin } from '@/lib/digital-twin';
import { RiskBadge } from '@/components/RiskBadge';
import { Input } from '@/components/ui/input';

export default function RoadList() {
  const navigate = useNavigate();
  const { data: roads, loading } = useAllRoads();
  
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!roads) return [];
    const q = search.toLowerCase();
    return roads.filter(r => r.road_name.toLowerCase().includes(q) || r.location.toLowerCase().includes(q));
  }, [roads, search]);

  if (loading) return <div className="p-8">Loading roads...</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Road Segments</h1>
          <p className="text-sm text-muted-foreground mt-1">{roads.length} monitored segments</p>
        </div>
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search roads..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-9 bg-card border-border"
          />
        </div>
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card border border-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left p-3 text-xs font-mono uppercase tracking-widest text-muted-foreground">Road</th>
              <th className="text-left p-3 text-xs font-mono uppercase tracking-widest text-muted-foreground">Location</th>
              <th className="text-right p-3 text-xs font-mono uppercase tracking-widest text-muted-foreground">Condition</th>
              <th className="text-right p-3 text-xs font-mono uppercase tracking-widest text-muted-foreground">Traffic</th>
              <th className="text-center p-3 text-xs font-mono uppercase tracking-widest text-muted-foreground">Risk</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((road, i) => {
              const twin = createDigitalTwin(road);
              return (
                <motion.tr
                  key={road.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.02 }}
                  onClick={() => navigate(`/roads/${road.id}`)}
                  className="border-b border-border last:border-0 hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <td className="p-3 font-medium text-foreground">{road.road_name}</td>
                  <td className="p-3 text-muted-foreground">{road.location}</td>
                  <td className="p-3 text-right font-mono text-foreground">{road.current_condition_index}</td>
                  <td className="p-3 text-right font-mono text-muted-foreground">{road.traffic_volume.toLocaleString()}</td>
                  <td className="p-3 text-center"><RiskBadge level={twin.risk_level} /></td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
