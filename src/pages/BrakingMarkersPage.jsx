import { useEffect, useState } from "react";
import {
  createBrakingMarker,
  deleteBrakingMarker,
  fetchBrakingMarkers,
  fetchCars,
  fetchTracks,
} from "../api.js";

const EMPTY_FORM = { label: "", distance_m: "", brake_speed_kmh: "", notes: "" };

export default function BrakingMarkersPage() {
  const [tracks, setTracks] = useState([]);
  const [cars, setCars] = useState([]);
  const [trackId, setTrackId] = useState("");
  const [carId, setCarId] = useState("");
  const [markers, setMarkers] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState(null);
  const [loadingOptions, setLoadingOptions] = useState(true);

  useEffect(() => {
    Promise.all([fetchTracks(), fetchCars()])
      .then(([trackList, carList]) => {
        setTracks(trackList);
        setCars(carList);
        setError(null);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingOptions(false));
  }, []);

  const hasSelection = Boolean(trackId && carId);

  const reloadMarkers = async () => {
    if (!hasSelection) return;
    try {
      setMarkers(await fetchBrakingMarkers(trackId, carId));
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    if (!hasSelection) {
      setMarkers([]);
      return;
    }
    let cancelled = false;
    fetchBrakingMarkers(trackId, carId)
      .then((list) => {
        if (!cancelled) {
          setMarkers(list);
          setError(null);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [trackId, carId, hasSelection]);

  const updateField = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }));
  };

  const canSubmit = hasSelection && form.label.trim() && form.distance_m !== "";

  const handleAdd = async (event) => {
    event.preventDefault();
    if (!canSubmit) return;
    try {
      await createBrakingMarker({
        track_id: trackId,
        car_id: carId,
        label: form.label.trim(),
        distance_m: Number(form.distance_m),
        brake_speed_kmh: form.brake_speed_kmh === "" ? null : Number(form.brake_speed_kmh),
        notes: form.notes.trim() || null,
      });
      setForm(EMPTY_FORM);
      await reloadMarkers();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (marker) => {
    if (!window.confirm(`Supprimer le repère "${marker.label}" ?`)) return;
    try {
      await deleteBrakingMarker(marker.id);
      await reloadMarkers();
    } catch (err) {
      setError(err.message);
    }
  };

  const gameCars = cars.filter((car) => car.source === "game");
  const customCars = cars.filter((car) => car.source === "custom");

  if (!loadingOptions && (tracks.length === 0 || cars.length === 0) && !error) {
    return (
      <section className="page">
        <h1>Repères de freinage</h1>
        <p className="muted">
          Ajoutez d'abord au moins un circuit et une voiture pour pouvoir enregistrer des repères.
        </p>
      </section>
    );
  }

  return (
    <section className="page">
      <h1>Repères de freinage</h1>
      <p className="muted">Choisissez un circuit et une voiture pour voir ou ajouter leurs repères.</p>

      <div className="selectors">
        <label>
          <span>Circuit</span>
          <select value={trackId} onChange={(event) => setTrackId(event.target.value)}>
            <option value="">Choisir un circuit</option>
            {tracks.map((track) => (
              <option key={track.id} value={track.id}>
                {track.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Voiture</span>
          <select value={carId} onChange={(event) => setCarId(event.target.value)}>
            <option value="">Choisir une voiture</option>
            <optgroup label="Voitures du jeu">
              {gameCars.map((car) => (
                <option key={car.id} value={car.id}>
                  {car.name}
                </option>
              ))}
            </optgroup>
            <optgroup label="Equipes custom">
              {customCars.map((car) => (
                <option key={car.id} value={car.id}>
                  {car.name} - {car.team_name}
                </option>
              ))}
            </optgroup>
          </select>
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      {hasSelection && (
        <>
          <form className="marker-form" onSubmit={handleAdd}>
            <input
              type="text"
              placeholder="Virage, ex. Virage 1"
              value={form.label}
              onChange={updateField("label")}
              aria-label="Nom du virage"
            />
            <input
              type="number"
              min="0"
              placeholder="Distance (m)"
              value={form.distance_m}
              onChange={updateField("distance_m")}
              aria-label="Distance depuis la ligne de départ en mètres"
            />
            <input
              type="number"
              min="1"
              placeholder="Vitesse de freinage (km/h)"
              value={form.brake_speed_kmh}
              onChange={updateField("brake_speed_kmh")}
              aria-label="Vitesse de freinage en km/h"
            />
            <input
              type="text"
              placeholder="Notes (optionnel)"
              value={form.notes}
              onChange={updateField("notes")}
              aria-label="Notes"
            />
            <button type="submit" className="primary-button" disabled={!canSubmit}>
              Ajouter le repère
            </button>
          </form>

          {markers.length === 0 ? (
            <p className="muted">Aucun repère pour cette voiture sur ce circuit.</p>
          ) : (
            <table className="markers-table">
              <thead>
                <tr>
                  <th>Virage</th>
                  <th>Distance</th>
                  <th>Vitesse de freinage</th>
                  <th>Notes</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {markers.map((marker) => (
                  <tr key={marker.id}>
                    <td>{marker.label}</td>
                    <td>{marker.distance_m} m</td>
                    <td>{marker.brake_speed_kmh ? `${marker.brake_speed_kmh} km/h` : "-"}</td>
                    <td>{marker.notes || "-"}</td>
                    <td className="right">
                      <button type="button" className="danger-button" onClick={() => handleDelete(marker)}>
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </section>
  );
}
