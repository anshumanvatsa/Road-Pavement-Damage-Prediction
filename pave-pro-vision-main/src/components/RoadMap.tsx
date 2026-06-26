import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

type Props = {
  latitude: number
  longitude: number
  onSelect: (lat: number, lng: number) => void
}

const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41]
})

function MapClickHandler({ onSelect }: { onSelect: Props["onSelect"] }) {
  useMapEvents({
    click(e) {
      onSelect(e.latlng.lat, e.latlng.lng)
    }
  })
  return null
}

export default function RoadMap({ latitude, longitude, onSelect }: Props) {

  return (
    <MapContainer
      center={[latitude || 20.5937, longitude || 78.9629]}
      zoom={5}
      style={{ height: "350px", width: "100%", borderRadius: "10px" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {latitude && longitude && (
        <Marker position={[latitude, longitude]} icon={markerIcon} />
      )}

      <MapClickHandler onSelect={onSelect} />

    </MapContainer>
  )
}
