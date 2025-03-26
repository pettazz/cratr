import { 
  useState, 
  useEffect 
} from 'react';
import { LatLngLiteral } from 'leaflet';

const defaultLatLng: LatLngLiteral = { lat: 0, lng: 0 };

export function useLocation() {
  const [isLocating, setIsLocating] = useState<boolean>(true);
  const [location, setLocation] = useState<LatLngLiteral>(defaultLatLng);
  const [locationError, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      console.error("Browser has no geolocation support");
      setError("Your device or browser does not support location services");
      setIsLocating(false);

      return;
    }

    navigator.geolocation.getCurrentPosition((pos: GeolocationPosition) => {
      setLocation({ 
        lat: pos.coords.latitude, 
        lng: pos.coords.longitude 
      });
      setIsLocating(false);
    }, (err) => {
      console.error(err);

      let msg = "There was a problem finding your location";
      if ("code" in err && err.code == 1) {
        msg = "Cratr does not have permission to use location services";
      }

      setError(msg);
      setIsLocating(false);
    });
  }, []);

  return { isLocating, location, locationError };
}