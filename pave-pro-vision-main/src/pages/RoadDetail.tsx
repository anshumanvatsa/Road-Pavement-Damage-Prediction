import { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Thermometer, Droplets, CloudRain, Truck, Activity } from 'lucide-react';
import { getRoad, getPredictions, getDigitalTwinForRoad } from '@/lib/store';
import { RiskBadge } from '@/components/RiskBadge';
import { Button } from '@/components/ui/button';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function RoadDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const road = useMemo(() => getRoad(id!), [id]);
  const predictions = useMemo(() => getPredictions(id!), [id]);
  const twin = useMemo(() => getDigitalTwinForRoad(id!), [id]);

  if (!road || !twin) {
    return <div className="text-center py-20 text-muted-foreground">Road not found</div>;
  }

  const chartData = [
    { month: 'Current', condition: road.current_condition_index },
    ...predictions.map(p => ({ month: `+${p.month_offset}m`, condition: p.predicted_condition_index })),
  ];

  const metrics = [
    { label: 'Temperature', value: `${road.temperature}°C`, icon: Thermometer },
    { label: 'Humidity', value: `${road.humidity}%`, icon: Droplets },
    { label: 'Rainfall', value: `${road.rainfall} mm`, icon: CloudRain },
    { label: 'Heavy Vehicles', value: `${road.heavy_vehicle_percentage}%`, icon: Truck },
  ];

  return (
    <div>
      <Button variant="ghost" onClick={() => navigate(-1)} className="mb-4 text-muted-foreground hover:text-foreground">
        <ArrowLeft className="w-4 h-4 mr-2" /> Back
      </Button>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{road.road_name}</h1>
          <p className="text-sm text-muted-foreground">{road.location} · {road.latitude.toFixed(4)}, {road.longitude.toFixed(4)}</p>
        </div>
        <RiskBadge level={twin.risk_level} className="text-sm" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {metrics.map(({ label, value, icon: Icon }) => (
          <div key={label} className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Icon className="w-4 h-4 text-primary" />
              <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">{label}</span>
            </div>
            <p className="text-xl font-bold font-mono text-foreground">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="lg:col-span-2 bg-card border border-border rounded-lg p-5">
          <h3 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">6-Month Condition Forecast</h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="condGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(185, 65%, 48%)" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="hsl(185, 65%, 48%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" stroke="hsl(215, 15%, 55%)" fontSize={11} tickLine={false} />
              <YAxis stroke="hsl(215, 15%, 55%)" fontSize={11} tickLine={false} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: 'hsl(220, 22%, 10%)', border: '1px solid hsl(220, 18%, 18%)', borderRadius: 8, fontSize: 12 }} />
              <Area type="monotone" dataKey="condition" stroke="hsl(185, 65%, 48%)" fill="url(#condGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }} className="bg-card border border-border rounded-lg p-5">
          <h3 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">Digital Twin</h3>
          <div className="space-y-4">
            <div>
              <p className="text-xs text-muted-foreground mb-1">Current Condition</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${twin.current_state}%` }} />
                </div>
                <span className="text-sm font-mono text-foreground w-12 text-right">{twin.current_state}</span>
              </div>
            </div>
            <div>
              <p className="text-xs text-muted-foreground mb-1">Predicted Condition</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full rounded-full bg-risk-medium transition-all" style={{ width: `${twin.predicted_state}%` }} />
                </div>
                <span className="text-sm font-mono text-foreground w-12 text-right">{twin.predicted_state}</span>
              </div>
            </div>
            <div className="pt-2 border-t border-border">
              <p className="text-xs text-muted-foreground mb-2">Recommendation</p>
              <p className="text-sm text-foreground">{twin.maintenance_recommendation}</p>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="bg-card border border-border rounded-lg p-5">
        <h3 className="text-sm font-mono uppercase tracking-widest text-muted-foreground mb-4">Monthly Predictions</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {predictions.map(p => (
            <div key={p.id} className="bg-muted/50 border border-border rounded-lg p-3 text-center">
              <p className="text-xs text-muted-foreground mb-1">{p.prediction_date}</p>
              <p className="text-lg font-bold font-mono text-foreground">{p.predicted_condition_index}</p>
              <p className="text-xs text-muted-foreground mb-2">Degradation: {p.predicted_degradation}</p>
              <RiskBadge level={p.risk_level} />
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
