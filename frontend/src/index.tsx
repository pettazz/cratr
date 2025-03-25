import { createRoot } from 'react-dom/client'
import 'tailwindcss/tailwind.css'
import "leaflet/dist/leaflet.css";

import "app.css";
import App from 'components/App'

const container = document.getElementById('root') as HTMLDivElement
const root = createRoot(container)

root.render(<App />)
