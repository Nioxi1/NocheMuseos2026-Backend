# Fix CORS and Backend Endpoints

## Goal Description
Resolve the CORS issues, add a backend autocomplete endpoint, adjust the frontend to use backend proxies for geocoding and autocomplete, and fix the undefined `puntoPartida` variable in `FormularioRestricciones.tsx`.

## User Review Required
[!IMPORTANT] The frontend will switch from direct Nominatim calls to a backend proxy. Ensure the backend is running on `http://localhost:8000` and that the frontend's API base URL points there.

## Open Questions
- Do you prefer the autocomplete endpoint to be a GET (`/api/autocomplete?query=...`) as implemented, or a POST with JSON payload?
- Should we add any rate limiting or caching for the Nominatim requests on the backend?

## Proposed Changes
---
### Backend (`backend/main.py`)
#### [MODIFY] [backend/main.py](file:///c:/Users/20190/OneDrive/Documentos/NocheMuseosIA/NocheMuseos2026-Backend/backend/main.py)
- Ensure `requests` is imported (already added).
- Confirm CORS middleware is correctly configured (already present).
- Add a new GET endpoint `/api/autocomplete` that proxies Nominatim requests and returns JSON suggestions.
- Keep existing `/api/geocode` and `/api/rutas` unchanged.

---
### Backend (`backend/agentes/AgenteTransporte.py`)
#### [MODIFY] [AgenteTransporte.py](file:///c:/Users/20190/OneDrive/Documentos/NocheMuseosIA/NocheMuseos2026-Backend/backend/agentes/AgenteTransporte.py)
- No changes needed; already uses `requests` for OSRM.

---
### Frontend (`src/components/MapaReal.tsx`)
#### [MODIFY] [MapaReal.tsx](file:///c:/Users/20190/OneDrive/Documentos/NocheMuseosIA/NocheMuseos2026-Frontend/src/components/MapaReal.tsx)
- Replace direct `fetch` calls to Nominatim with calls to our backend endpoint:
  ```ts
  const url = `${API_BASE}/api/autocomplete?query=${encodeURIComponent(search)}`;
  ```
- Update `fetchStartSuggestions` and `fetchCustomSuggestions` accordingly.
- Ensure error handling for network errors.

---
### Frontend (`src/components/FormularioRestricciones.tsx`)
#### [MODIFY] [FormularioRestricciones.tsx](file:///c:/Users/20190/OneDrive/Documentos/NocheMuseosIA/NocheMuseos2026-Frontend/src/components/FormularioRestricciones.tsx)
- Define `puntoPartida` state using `useState<{lat:number,lng:number}>` or retrieve it from the global app state.
- Pass the correct variable to the map component when navigating to `/mapa`.
- Remove the reference error.

---
### Frontend (`src/store/appState.ts`)
#### [MODIFY] [appState.ts](file:///c:/Users/20190/OneDrive/Documentos/NocheMuseosIA/NocheMuseos2026-Frontend/src/store/appState.ts)
- Export a selector or setter for `puntoPartida` if not already present.

## Verification Plan
### Automated Tests
- Run unit tests for backend (if any) and manually test `/api/autocomplete` with sample queries.
- Use the browser to load the map page, type a location, and verify suggestions appear.
- Verify that clicking a museum marker displays info and add-to-visit works.
- Confirm no console errors for `puntoPartida`.

### Manual Verification
- Run the FastAPI backend and the Vite dev server.
- Navigate to the restrictions form, fill in data, submit, and ensure the map loads correctly centered on the entered start point.
- Test adding multiple museums and ensure the route calculation works without errors.
