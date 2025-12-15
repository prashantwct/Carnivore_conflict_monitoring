import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; // Import Leaflet CSS
import './App.css'; // For custom styling

// Placeholder data for initial map display
const initialIncidents = [
  { id: 1, lat: 21.1466, lng: 79.0888, type: "P-1 CRITICAL", location: "Nagpur Village Edge", status: "Reported" },
  { id: 2, lat: 21.0, lng: 79.5, type: "P-3 Routine", location: "Forest Scat Site", status: "Resolved" },
];

function App() {
  const [incidents, setIncidents] = useState(initialIncidents);
  const [selectedIncident, setSelectedIncident] = useState(null);

  // Nagpur coordinates as the center of the map
  const center = [21.1466, 79.0888]; 

  // Function to fetch real data would go here (using axios and our API endpoints)
  // const fetchIncidents = () => { /* ... API call to /api/v1/incidents ... */ };

  // Simple function to get marker color based on priority
  const getMarkerColor = (priority) => {
    if (priority.startsWith('P-1')) return 'red';
    if (priority.startsWith('P-2')) return 'orange';
    return 'blue';
  };

  return (
    <div className="dashboard-layout">
      {/* 1. Header/Alerts Panel */}
      <header className="header-panel">
        <h1>🐯 Conflict Management Dashboard</h1>
        <div className="alert-count">
          P-1 CRITICAL Incidents: <span className="p1-counter">{incidents.filter(i => i.type.startsWith('P-1') && i.status === 'Reported').length}</span>
        </div>
      </header>

      {/* 2. Main Content Area */}
      <div className="main-content">
        
        {/* Map Container (Center Area) */}
        <div className="map-container">
          {/* Display of the core map area, using Leaflet  */}
          <MapContainer center={center} zoom={10} style={{ height: '100%', width: '100%' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
            />
            {incidents.map(incident => (
              <Marker 
                key={incident.id} 
                position={[incident.lat, incident.lng]}
                // You would need to use a custom icon/color plugin for better visualization
                onClick={() => setSelectedIncident(incident)}
              >
                <Popup>
                  <b>Incident #{incident.id}</b><br />
                  Type: {incident.type}<br />
                  Status: {incident.status}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Incident Feed (Left Panel) */}
        <aside className="feed-panel">
          <h2>Incident Feed</h2>
          {incidents.map(incident => (
            <div 
              key={incident.id} 
              className={`incident-card ${incident.type.toLowerCase().replace(' ', '-')}`}
              onClick={() => setSelectedIncident(incident)}
              style={{ borderLeftColor: getMarkerColor(incident.type) }}
            >
              <p>#{incident.id} - <b>{incident.type}</b></p>
              <p>{incident.location}</p>
              <small>Status: {incident.status}</small>
            </div>
          ))}
        </aside>

        {/* Detail/Action Panel (Conditional) */}
        {selectedIncident && (
          <div className="detail-panel">
            <h2>Incident Detail #{selectedIncident.id}</h2>
            <p>Type: <b>{selectedIncident.type}</b></p>
            <p>Location: {selectedIncident.location}</p>
            <p>Status: {selectedIncident.status}</p>
            {selectedIncident.type.startsWith('P-1') && (
              <div className="action-buttons">
                <button className="btn-assign">Assign Team</button>
                <button className="btn-resolve">Resolve Incident</button>
              </div>
            )}
            <button onClick={() => setSelectedIncident(null)}>Close</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
