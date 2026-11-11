import { useEffect, useState } from "react";
import { createCar, deleteCar, fetchCars } from "../api.js";

const EMPTY_FORM = { name: "", category: "", source: "game", team_name: "" };

export default function CarsPage() {
  const [cars, setCars] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const reload = async () => {
    try {
      setCars(await fetchCars());
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

  const updateField = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }));
  };

  const canSubmit =
    form.name.trim() &&
    form.category.trim() &&
    (form.source === "game" || form.team_name.trim());

  const handleAdd = async (event) => {
    event.preventDefault();
    if (!canSubmit) return;
    try {
      await createCar({
        name: form.name.trim(),
        category: form.category.trim(),
        source: form.source,
        team_name: form.source === "custom" ? form.team_name.trim() : null,
      });
      setForm(EMPTY_FORM);
      await reload();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (car) => {
    if (!window.confirm(`Supprimer la voiture "${car.name}" et tous ses repères ?`)) return;
    try {
      await deleteCar(car.id);
      await reload();
    } catch (err) {
      setError(err.message);
    }
  };

  const gameCars = cars.filter((car) => car.source === "game");
  const customCars = cars.filter((car) => car.source === "custom");

  return (
    <section className="page">
      <h1>Voitures</h1>
      <p className="muted">Voitures du jeu et voitures des équipes custom.</p>

      <form className="car-form" onSubmit={handleAdd}>
        <input
          type="text"
          placeholder="Modèle, ex. Porsche 963"
          value={form.name}
          onChange={updateField("name")}
          aria-label="Modèle de la voiture"
        />
        <input
          type="text"
          placeholder="Catégorie, ex. Hypercar"
          value={form.category}
          onChange={updateField("category")}
          aria-label="Catégorie"
        />
        <select value={form.source} onChange={updateField("source")} aria-label="Origine">
          <option value="game">Voiture du jeu</option>
          <option value="custom">Equipe custom</option>
        </select>
        {form.source === "custom" && (
          <input
            type="text"
            placeholder="Nom de l'équipe"
            value={form.team_name}
            onChange={updateField("team_name")}
            aria-label="Nom de l'équipe"
          />
        )}
        <button type="submit" className="primary-button" disabled={!canSubmit}>
          Ajouter
        </button>
      </form>

      {error && <p className="error">{error}</p>}
      {loading && <p className="muted">Chargement...</p>}

      <h2>Voitures du jeu ({gameCars.length})</h2>
      <CarList cars={gameCars} onDelete={handleDelete} emptyText="Aucune voiture du jeu." />

      <h2>Equipes custom ({customCars.length})</h2>
      <CarList cars={customCars} onDelete={handleDelete} emptyText="Aucune équipe custom." />
    </section>
  );
}

function CarList({ cars, onDelete, emptyText }) {
  if (cars.length === 0) return <p className="muted">{emptyText}</p>;
  return (
    <ul className="list">
      {cars.map((car) => (
        <li key={car.id} className="list-item">
          <div>
            <strong>{car.name}</strong>
            <span className="muted">
              {" "}
              - {car.category}
              {car.team_name ? ` - ${car.team_name}` : ""}
            </span>
          </div>
          <button type="button" className="danger-button" onClick={() => onDelete(car)}>
            Supprimer
          </button>
        </li>
      ))}
    </ul>
  );
}
