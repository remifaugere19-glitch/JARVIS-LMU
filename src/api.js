import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function fetchTracks() {
  const { data, error } = await supabase.from("tracks").select("*").order("name");
  if (error) throw new Error(error.message);
  return data ?? [];
}

export async function createTrack(name) {
  const { error } = await supabase.from("tracks").insert({ name });
  if (error) throw new Error(error.message);
}

export async function deleteTrack(id) {
  const { error } = await supabase.from("tracks").delete().eq("id", id);
  if (error) throw new Error(error.message);
}

export async function fetchCars() {
  const { data, error } = await supabase
    .from("cars")
    .select("*")
    .order("source")
    .order("name");
  if (error) throw new Error(error.message);
  return data ?? [];
}

export async function createCar(car) {
  const { error } = await supabase.from("cars").insert(car);
  if (error) throw new Error(error.message);
}

export async function deleteCar(id) {
  const { error } = await supabase.from("cars").delete().eq("id", id);
  if (error) throw new Error(error.message);
}

export async function fetchBrakingMarkers(trackId, carId) {
  const { data, error } = await supabase
    .from("braking_markers")
    .select("*")
    .eq("track_id", trackId)
    .eq("car_id", carId)
    .order("distance_m");
  if (error) throw new Error(error.message);
  return data ?? [];
}

export async function createBrakingMarker(marker) {
  const { error } = await supabase.from("braking_markers").insert(marker);
  if (error) throw new Error(error.message);
}

export async function deleteBrakingMarker(id) {
  const { error } = await supabase.from("braking_markers").delete().eq("id", id);
  if (error) throw new Error(error.message);
}
