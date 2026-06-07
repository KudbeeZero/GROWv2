import { apiFetch } from "./client";
import type { Strain, LineageType, Rarity } from "@/lib/types";

export interface StrainFilters {
  catalog_only?: boolean;
  q?: string;
  rarity?: Rarity;
  lineage_type?: LineageType;
  min_thc?: number;
  max_thc?: number;
  min_indica?: number;
  max_indica?: number;
}

export const strains = {
  list: (filters: StrainFilters = {}) =>
    apiFetch<Strain[]>("/strains", { query: filters as Record<string, string | number | boolean | undefined> }),

  get: (strainId: string) => apiFetch<Strain>(`/strains/${strainId}`),

  favorites: (playerId: string) => apiFetch<Strain[]>(`/players/${playerId}/favorites`),

  addFavorite: (playerId: string, strainId: string) =>
    apiFetch<{ favorited: boolean }>(
      `/players/${playerId}/strains/${strainId}/favorite`,
      { method: "POST" },
    ),

  removeFavorite: (playerId: string, strainId: string) =>
    apiFetch<{ favorited: boolean }>(
      `/players/${playerId}/strains/${strainId}/favorite`,
      { method: "DELETE" },
    ),

  stabilize: (playerId: string, strainId: string, rng_seed?: number) =>
    apiFetch<Strain>(`/players/${playerId}/strains/${strainId}/stabilize`, {
      method: "POST",
      body: { rng_seed },
    }),

  mint: (playerId: string, strainId: string) =>
    apiFetch<Strain>(`/players/${playerId}/strains/${strainId}/mint`, { method: "POST" }),
};
