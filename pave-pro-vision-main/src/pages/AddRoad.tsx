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

  const update = (key: string, value: string) => {
    setForm(prev => ({ ...prev, [key]: key === 'road_name' || key === 'location' ? value : Number(value) }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.road_name || !form.location) {
      toast.error('Please fill in road name and location');
      return;
    }
    const road = addRoad(form);
    toast.success(`${road.road_name} added successfully`);
    navigate(`/roads/${road.id}`);
  };

  const fields = [
    { key: 'road_name', label: 'Road Name', type: 'text' },
    { key: 'location', label: 'Location', type: 'text' },
    { key: 'latitude', label: 'Latitude', type: 'number' },
    { key: 'longitude', label: 'Longitude', type: 'number' },
    { key: 'current_condition_index', label: 'Condition Index (0-100)', type: 'number' },
    { key: 'traffic_volume', label: 'Traffic Volume', type: 'number' },
    { key: 'heavy_vehicle_percentage', label: 'Heavy Vehicle %', type: 'number' },
    { key: 'rainfall', label: 'Rainfall (mm)', type: 'number' },
    { key: 'temperature', label: 'Temperature (°C)', type: 'number' },
    { key: 'humidity', label: 'Humidity (%)', type: 'number' },
  ];

  return (
    <div className="max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Add Road Segment</h1>
        <p className="text-sm text-muted-foreground mt-1">Register a new road for monitoring</p>
      </div>

      <motion.form initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} onSubmit={handleSubmit} className="bg-card border border-border rounded-lg p-6 space-y-5">
        <div className="mb-4">
          <Label className="block text-sm font-medium mb-2">
            Select location on map
          </Label>
          <MapContainer
            center={[form.latitude || 20.5937, form.longitude || 78.9629]}
            zoom={5}
            style={{ height: '350px', width: '100%', borderRadius: '10px' }}
          >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <MapClickHandler
              onSelect={(lat, lng, road_name, location) =>
                setForm((prev) => ({
                  ...prev,
                  latitude: lat,
                  longitude: lng,
                  ...(road_name !== undefined && { road_name }),
                  ...(location !== undefined && { location }),
                }))
              }
            />
          </MapContainer>
          <p className="text-xs text-muted-foreground mt-1">
            Click anywhere on map to auto-fill coordinates
          </p>
        </div>
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
        <div className="flex gap-3 pt-2">
          <Button type="submit">Add Road Segment</Button>
          <Button type="button" variant="ghost" onClick={() => navigate('/roads')} className="text-muted-foreground">Cancel</Button>
        </div>
      </motion.form>
    </div>
  );
}
