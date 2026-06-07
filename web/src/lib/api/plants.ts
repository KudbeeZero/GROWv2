import { apiFetch } from "./client";
import type { Plant, PlantState, PlantEvent, Harvest } from "@/lib/types";

export const plants = {
  list: (playerId: string) => apiFetch<Plant[]>(`/players/${playerId}/plants`),

  state: (playerId: string, plantId: string) =>
    apiFetch<PlantState>(`/players/${playerId}/plants/${plantId}/state`),

  events: (plantId: string, limit = 50) =>
    apiFetch<PlantEvent[]>(`/plants/${plantId}/events`, { query: { limit } }),

  plant: (playerId: string, seedId: string, podId: string) =>
    apiFetch<Plant>(`/players/${playerId}/plant`, {
      method: "POST",
      body: { seed_id: seedId, pod_id: podId },
    }),

  water: (playerId: string, plantId: string, amount?: number) =>
    apiFetch<Plant>(`/players/${playerId}/plants/${plantId}/water`, {
      method: "POST",
      body: { amount },
    }),

  feed: (playerId: string, plantId: string, amount?: number) =>
    apiFetch<Plant>(`/players/${playerId}/plants/${plantId}/feed`, {
      method: "POST",
      body: { amount },
    }),

  treatPests: (playerId: string, plantId: string) =>
    apiFetch<Plant>(`/players/${playerId}/plants/${plantId}/treat-pests`, {
      method: "POST",
    }),

  treatDisease: (playerId: string, plantId: string) =>
    apiFetch<Plant>(`/players/${playerId}/plants/${plantId}/treat-disease`, {
      method: "POST",
    }),

  harvest: (
    playerId: string,
    plantId: string,
    opts: { weight_g?: number; quality?: number; sell?: boolean } = {},
  ) =>
    apiFetch<Harvest>(`/players/${playerId}/plants/${plantId}/harvest`, {
      method: "POST",
      body: opts,
    }),

  mintHarvest: (playerId: string, harvestId: string) =>
    apiFetch<Harvest>(`/players/${playerId}/harvests/${harvestId}/mint`, {
      method: "POST",
    }),
};
