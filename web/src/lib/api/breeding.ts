import { apiFetch } from "./client";
import type { Strain } from "@/lib/types";

export const breeding = {
  breed: (
    playerId: string,
    parentAId: string,
    parentBId: string,
    opts: { name?: string; rng_seed?: number } = {},
  ) =>
    apiFetch<Strain>(`/players/${playerId}/breed`, {
      method: "POST",
      body: { parent_a_id: parentAId, parent_b_id: parentBId, ...opts },
    }),
};
