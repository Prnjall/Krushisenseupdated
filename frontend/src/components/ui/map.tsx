import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom SVG icon for a minimal aesthetic
const createCustomIcon = (color = '#000000') => {
  return L.divIcon({
    html: `
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1))">
        <path d="M21 10C21 17 12 23 12 23C12 23 3 17 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 21 10Z" fill="${color}" fill-opacity="0.2" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="10" r="3" fill="${color}" stroke="${color}" stroke-width="1.5"/>
      </svg>
    `,
    className: 'custom-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

const defaultIcon = createCustomIcon('#000000');

interface MapProps {
  center: [number, number]; // [lng, lat]
  zoom: number;
  children?: React.ReactNode;
  className?: string;
}

// Helper component to update map view when props change
function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([center[1], center[0]], zoom);
  }, [center, zoom, map]);
  return null;
}

export const Map: React.FC<MapProps> = ({ center, zoom, children, className = '' }) => {
  return (
    <div className={`h-full w-full ${className}`}>
      <MapContainer
        center={[center[1], center[0]]}
        zoom={zoom}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ChangeView center={center} zoom={zoom} />
        {children}
      </MapContainer>
    </div>
  );
};

interface MapMarkerProps {
  longitude: number;
  latitude: number;
  children?: React.ReactNode;
  icon?: L.DivIcon | L.Icon;
}

export const MapMarker: React.FC<MapMarkerProps> = ({ longitude, latitude, children, icon }) => {
  return (
    <Marker position={[latitude, longitude]} icon={icon || defaultIcon}>
      {children}
    </Marker>
  );
};

export const MarkerContent: React.FC<{ children: React.ReactNode }> = ({ children }) => {

  return null;
};



export const MarkerLabel: React.FC<{ children: React.ReactNode; position?: string }> = ({ children }) => {
  return null; // Tooltip could be used here
};

export const MarkerPopup: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => {
  return (
    <Popup className={className}>
      {children}
    </Popup>
  );
};
