import { useEffect, useState } from "react";
import { createTrack, deleteTrack, fetchTracks } from "../api.js";

export default function TracksPage() {
  const [tracks, setTracks] = useState([]);
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const reload = async () => {
    try {
      setTracks(await fetchTracks());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
  }, []);

  const handleAdd = async (event) => {
    event.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    try {
      await createTrack(trimmed);
      setName("");
      await reload();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (track) => {
    if (!window.confirm(`Supprimer le circuit "${track.name}" et tous ses repères ?`)) return;
    try {
      await deleteTrack(track.id);
      await reload();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <section className="page">
      <h1>Circuits</h1>
      <p className="muted">Les circuits de Le Mans Ultimate sur lesquels vous enregistrez des repères.</p>

      <form className="inline-form" onSubmit={handleAdd}>
        <input
          type="text"
          placeholder="Nom du circuit, ex. Circuit de Spa-Francorchamps"
          value={name}
          onChange={(event) => setName(event.target.value)}
          aria-label="Nom du circuit"
        />
        <button type="submit" className="primary-button" disabled={!name.trim()}>
          Ajouter
        </button>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p className="muted">Chargement...</p>}
      {!loading && tracks.length === 0 && <p className="muted">Aucun circuit pour le moment.</p>}

      <ul className="list">
        {tracks.map((track) => (
          <li key={track.id} className="list-item">
            <span>{track.name}</span>
            <button type="button" className="danger-button" onClick={() => handleDelete(track)}>
              Supprimer
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
