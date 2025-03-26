import React, { 
  useCallback, 
  useEffect, 
  useMemo, 
  useState 
} from 'react';
import { 
  Icon, 
  LatLngLiteral 
} from 'leaflet';
import { 
  MapContainer,
  Marker,
  Popup,
  TileLayer, 
  useMap,
  useMapEvents 
} from 'react-leaflet';

import { classificationMap, resourceList } from 'utils';
import { useLocation } from 'utils/useLocation';
import markerIconImg from 'assets/marker-icon.png';

const defaultLocation: LatLngLiteral = { lat: 29.56, lng: -95.09 },
      maxSearchRadius: number = 500, 
      defaultZoom: number = 8,
      apiURL: string = process.env.NODE_ENV == "production" ? 
        'https://api.cratr.rocks/meteorites':
        '/meteorites';

const markerIcon = new Icon({
  iconUrl: markerIconImg,
  iconSize: [25, 25]
});

type Meteorite = {
  id: number
  name: string
  class: string
  distance: number
  mass: number
  year: number
  lat: number
  lon: number
};

function MeteoriteMarkers(selectedResourcesMap: any) {
  // todo: replace passing this map around with proper state
  const selectedResources = selectedResourcesMap["selectedResources"];
  const [meteorites, setMeteorites] = useState<Meteorite[]>([]);
  const map = useMap();

  const findRadius = () => {
    const bounds = map.getBounds(),
          vert = bounds.getNorthWest().distanceTo(bounds.getSouthWest()) * 0.000621371,
          horiz = bounds.getNorthWest().distanceTo(bounds.getNorthEast()) * 0.000621371,
          minRadius = Math.min(vert, horiz) / 2;

    return minRadius > maxSearchRadius ? maxSearchRadius : minRadius;
  }

  const updateMarkers = () => {
    const currentLocation = map.getCenter(),
          currentLocationRounded = {
            // 11.1 km accuracy at 1 decimal place
            lat: currentLocation.lat.toFixed(1),
            lng: currentLocation.lng.toFixed(1)
          };

    console.debug("requesting for", currentLocationRounded);
    fetch(`${apiURL}?lat=${currentLocationRounded.lat}&lon=${currentLocationRounded.lng}&radius=${findRadius()}`)
      .then((response) => response.json())
      .then((response) => {
        setMeteorites(response);
      });
  }

  useEffect(() => {
    updateMarkers();
  }, []);

  useMapEvents({
    moveend: updateMarkers,
    zoomend: updateMarkers
  });

  return (
    <React.Fragment>
      {meteorites.filter((meteorite: Meteorite) => { 
                    const cls = classificationMap.get(meteorite.class);
                    return cls && cls.resources.some(resource => selectedResources.get(resource)) })
                 .map((meteorite: Meteorite) => {
                    const cls = classificationMap.get(meteorite.class)

                    return (
                      <Marker 
                        icon={markerIcon}
                        key={meteorite.id}
                        position={{ lat: meteorite.lat, lng: meteorite.lon }}>
                        <Popup>
                          <strong>{meteorite.name}</strong> ({meteorite.year})<br />
                          <em>{meteorite.distance.toFixed(1)} miles from map center</em><br />
                          {cls ? cls.name : 'Unnamed Meteorite'}, {meteorite.mass} grams<br />
                          {cls && cls.resources.length > 0 ? 'Resources: ' + cls.resources.join(", ") : ''}
                        </Popup>
                      </Marker>
                    );
                  })}
    </React.Fragment>
  );
}

interface ResourceCheckboxProps {
  resource: string;
  isChecked: boolean;
  onChange: React.ChangeEventHandler;
  label: string;
}

function ResourceCheckbox({ resource, isChecked, onChange, label }: ResourceCheckboxProps) {
  return (
    <p>
      <input
        type="checkbox"
        id={`chx-resource-${resource}`}
        checked={isChecked}
        onChange={onChange}
      />
      <label htmlFor={`chx-resource-${resource}`}>{label}</label>
    </p>
  )
};

function App() {
  let { isLocating, location, locationError } = useLocation();

  const defaultResourceSelection = new Map(resourceList.map(r => [r, true])),
        [selectedResources, setSelectedResources] = useState(defaultResourceSelection);

  const updateResourceSelection = (resource: string) => {
    selectedResources.set(resource, !selectedResources.get(resource));
    setSelectedResources(selectedResources);
  };

  const displayMap = () => {
    if (isLocating) {
      return <div>locating...</div>
    }

    if (locationError) {
      location = defaultLocation;
    }

    return (
      <MapContainer
        center={location}
        zoom={defaultZoom}
        scrollWheelZoom={false}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MeteoriteMarkers selectedResources={selectedResources} />
      </MapContainer>
  )};

  return (
    <div>
      <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
        Cratr
      </h1>
      <div>{locationError ? 'Unable to use your location. ' : ''}Move or zoom the map to redo search.</div>
      {displayMap()}

      <div>
        <h3>Choose which resources to display</h3>
        {Array.from(selectedResources.keys(), String).map((resource: string) => {
          return (
            <ResourceCheckbox
              key={resource}
              resource={resource}
              isChecked={selectedResources.get(resource) ?? false}
              onChange={() => updateResourceSelection(resource)}
              label={resource} />
          );
        })}
      </div>
    </div>
  );
}

export default App;
