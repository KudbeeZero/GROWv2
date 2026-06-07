import { apiFetch } from "./client";
import type { Contract } from "@/lib/types";

export const contracts = {
  list: (playerId: string, status?: "open" | "fulfilled") =>
    apiFetch<Contract[]>(`/players/${playerId}/contracts`, { query: { status } }),

  offer: (playerId: string, rng_seed?: number) =>
    apiFetch<Contract>(`/players/${playerId}/contracts/offer`, {
      method: "POST",
      body: { rng_seed },
    }),

  fulfill: (playerId: string, contractId: string) =>
    apiFetch<Record<string, unknown>>(
      `/players/${playerId}/contracts/${contractId}/fulfill`,
      { method: "POST" },
    ),
};
