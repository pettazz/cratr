import { 
  useState, 
  useEffect 
} from 'react';

export function useLocation() {
  const [location, setLocation] = useState(null);
  const [locationError, setError] = useState(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      console.error("Browser has no geolocation support");
      setError({ code: 0, message: "Browser has no geolocation support" });

      return;
    }

    navigator.geolocation.getCurrentPosition((pos) => {
      const { latitude, longitude } = pos.coords;
      setLocation({ latitude, longitude });
    }, (err) => {
      console.error(err);
      setError(err);
    });
  }, []);

  return { location, locationError };
}