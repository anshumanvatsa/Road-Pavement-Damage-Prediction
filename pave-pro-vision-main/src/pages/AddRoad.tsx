import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MapContainer, TileLayer, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { addRoad } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { RiskBadge } from '@/components/RiskBadge';

const markerIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function MapClickHandler({
  onSelect,
}: {
  onSelect: (lat: number, lng: number, road_name?: string, location?: string) => void;
}) {
  const map = useMap();
  const markerRef = useRef<L.Marker | null>(null);

  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      onSelect(lat, lng);
      if (markerRef.current) {
        markerRef.current.setLatLng(e.latlng);
      } else {
        markerRef.current = L.marker(e.latlng, { icon: markerIcon }).addTo(map);
      }
      fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
        { headers: { Accept: 'application/json' } }
      )
        .then((res) => res.json())
        .then((data) => {
          const road_name =
            data?.address?.road ||
            data?.address?.highway ||
            data?.address?.neighbourhood ||
            data?.display_name ||
            '';
          const location =
            data?.address?.city ||
            data?.address?.town ||
            data?.address?.village ||
            data?.address?.state ||
            '';
          onSelect(lat, lng, road_name, location);
        })
        .catch(() => {});
    },
  });
  return null;
}

export default function AddRoad() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    road_name: '',
    location: '',
    latitude: 37.5,
    longitude: -122.2,
    current_condition_index: 75,
    traffic_volume: 5000,
    heavy_vehicle_percentage: 15,
    rainfall: 100,
    temperature: 22,
    humidity: 55,
  });

  const [livePrediction, setLivePrediction] = useState<{degradation: number, new_condition: number, risk_level: string} | null>(null);

  const fetchLivePrediction = async (currentForm: typeof form) => {
    try {
      const apiBase = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://127.0.0.1:8000/api');
      const res = await fetch(`${apiBase}/predict/custom`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          traffic_volume: currentForm.traffic_volume,
          heavy_vehicle_percentage: currentForm.heavy_vehicle_percentage,
          rainfall: currentForm.rainfall,
          temperature: currentForm.temperature,
          humidity: currentForm.humidity,
          current_condition: currentForm.current_condition_index
        })
      });
      if (res.ok) {
        const data = await res.json();
        setLivePrediction(data);
      }
    } catch (e) {
      console.error("Prediction fetch failed", e);
    }
  };

  const update = (key: string, value: string) => {
    const newForm = { ...form, [key]: key === 'road_name' || key === 'location' ? value : Number(value) };
    setForm(newForm);
    // Auto-update prediction when environmental inputs change
    if (['traffic_volume', 'heavy_vehicle_percentage', 'rainfall', 'temperature', 'humidity', 'current_condition_index'].includes(key)) {
      fetchLivePrediction(newForm);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.road_name || !form.location) {
      toast.error('Please fill in road name and location');
      return;
    }
    try {
      const road = await addRoad(form);
      toast.success(`${road.road_name} added successfully`);
      navigate(`/roads/${road.id}`);
    } catch (e) {
      toast.error('Failed to add road');
    }
  };

  const fields = [
    { key: 'road_name', label: 'Road Name', type: 'text' },
    { key: 'location', label: 'Location', type: 'text' },
    { key: 'latitude', label: 'Latitude', type: 'number' },
    { key: 'longitude', label: 'Longitude', type: 'number' },
    { key: 'current_condition_index', label: 'Condition Index (0-100)', type: 'number' },
    { key: 'traffic_volume', label: 'Traffic Volume', type: 'number' },
    { key: 'heavy_vehicle_percentage', label: 'Heavy %', type: 'number' },
    { key: 'rainfall', label: 'Rainfall (mm)', type: 'number' },
    { key: 'temperature', label: 'Temperature (°C)', type: 'number' },
    { key: 'humidity', label: 'Humidity (%)', type: 'number' },
  ];

  return (
    <div className="max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Live Road Map & Predictor</h1>
        <p className="text-sm text-muted-foreground mt-1">Pinpoint a location on the map to instantly predict its deterioration.</p>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
        
        {/* Map Section */}
        <div className="bg-card border border-border rounded-lg p-6">
          <Label className="block text-sm font-medium mb-2">
            Click map to pinpoint a road and predict
          </Label>
          <MapContainer
            center={[form.latitude || 20.5937, form.longitude || 78.9629]}
            zoom={5}
            style={{ height: '400px', width: '100%', borderRadius: '10px' }}
          >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <MapClickHandler
              onSelect={(lat, lng, road_name, location) => {
                const newForm = {
                  ...form,
                  latitude: lat,
                  longitude: lng,
                  ...(road_name !== undefined && { road_name }),
                  ...(location !== undefined && { location }),
                };
                setForm(newForm);
                fetchLivePrediction(newForm);
              }}
            />
          </MapContainer>
        </div>

        {/* Live Prediction Box */}
        {livePrediction && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-primary/10 border border-primary/20 rounded-lg p-5 flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-primary mb-1">Instant ML Prediction</h3>
              <p className="text-sm text-muted-foreground">Based on selected location features, road condition will drop by <span className="font-bold text-foreground">{livePrediction.degradation.toFixed(2)} points</span> over 6 months.</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-foreground">{livePrediction.new_condition.toFixed(1)} <span className="text-sm font-normal text-muted-foreground">/ 100</span></div>
              <RiskBadge level={livePrediction.risk_level as any} />
            </div>
          </motion.div>
        )}

        {/* Feature Editing Form */}
        <form onSubmit={handleSubmit} className="bg-card border border-border rounded-lg p-6 space-y-5">
          <h3 className="text-sm font-semibold mb-4">Edit Location Features & Save</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fields.map(({ key, label, type }) => (
              <div key={key} className={key === 'road_name' || key === 'location' ? 'md:col-span-2' : ''}>
                <Label className="text-xs font-mono uppercase tracking-widest text-muted-foreground">{label}</Label>
                <Input
                  type={type}
                  value={(form as any)[key]}
                  onChange={e => update(key, e.target.value)}
                  className="mt-1 bg-muted border-border"
                  step={type === 'number' ? 'any' : undefined}
                />
              </div>
            ))}
          </div>
          <div className="flex gap-3 pt-4">
            <Button type="submit">Save to Dashboard</Button>
            <Button type="button" variant="ghost" onClick={() => navigate('/roads')} className="text-muted-foreground">Cancel</Button>
          </div>
        </form>

      </motion.div>
    </div>
  );
}
