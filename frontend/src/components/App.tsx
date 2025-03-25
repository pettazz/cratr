import React, { 
  useCallback, 
  useEffect, 
  useMemo, 
  useState 
} from 'react';
import { 
  MapContainer,
  Marker,
  Popup,
  TileLayer, 
  useMap 
} from 'react-leaflet';

import { useLocation } from 'utils/useLocation'

function DisplayPosition({ map, center }) {
  const [position, setPosition] = useState(() => map.getCenter());

  const onResetClick = useCallback(() => {
    map.setView(getCenter);
  }, [map]);

  const onSearchMap = useCallback(() => {
    map.setView(center);
  }, [map]);

  const onMove = useCallback(() => {
    setPosition(map.getCenter());
  }, [map]);

  useEffect(() => {
    map.on('move', onMove);
    return () => {
      map.off('move', onMove);
    }
  }, [map, onMove]);

  return (
    <div className="mt-4 text-xl text-gray-500">
      <h2>Coordinates</h2>
      <p>latitude: {position.lat.toFixed(4)}</p>
      <p>longitude: {position.lng.toFixed(4)}{' '}</p>
      <button className="rounded-full text-white bg-indigo-500" onClick={onResetClick}>Reset Map</button>
      <button className="rounded-full text-white bg-indigo-500" onClick={onSearchMap}>Search within current map</button>
    </div>
  );
}

function App() {
  const [map, setMap] = useState(null);
  const { location, locationError } = useLocation();

  const displayMap = useMemo(() => {
    if (locationError) {
      console.log(locationError)
      let msg = "There was a problem finding your location";
      
      if ("code" in locationError){
        if (locationError.code == 0) msg = "Your device or browser does not support location services";
        if (locationError.code == 1) msg = "Cratr does not have permission to use location services";
      }

      return <div>uh oh no mappy: {msg}</div>;
    }

    if (!location) {
      return <div>locating...</div>
    }

    return (
      <MapContainer
        center={[location.latitude, location.longitude]}
        zoom="10"
        scrollWheelZoom={false}
        ref={setMap}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </MapContainer>
  )}, [map, location, locationError]);


  return (
    <div>
      <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
        cratr
      </h1>

      {map ? <DisplayPosition map={map} center={[location.latitude, location.longitude]} /> : null}
      {displayMap}
    </div>
  );
}

export default App;
