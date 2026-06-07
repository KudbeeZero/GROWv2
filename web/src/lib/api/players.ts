import { apiFetch } from "./client";
import type {
  Player,
  Wallet,
  LevelProgress,
  LedgerEntry,
  Achievement,
} from "@/lib/types";

export const players = {
  create: (username: string, email?: string) =>
    apiFetch<Player>("/players", { method: "POST", auth: false, body: { username, email } }),

  get: (playerId: string) => apiFetch<Player>(`/players/${playerId}`, { auth: true }),

  wallet: (playerId: string) =>
    apiFetch<Wallet>(`/players/${playerId}/wallet`, { auth: true }),

  level: (playerId: string) => apiFetch<LevelProgress>(`/players/${playerId}/level`),

  ledger: (playerId: string) =>
    apiFetch<LedgerEntry[]>(`/players/${playerId}/ledger`, { auth: true }),

  claimDaily: (playerId: string) =>
    apiFetch<{ amount: number; balance: number }>(`/players/${playerId}/daily`, {
      method: "POST",
    }),

  achievements: (playerId: string) =>
    apiFetch<Achievement[]>(`/players/${playerId}/achievements`, { auth: true }),

  claimAchievement: (playerId: string, key: string) =>
    apiFetch<{ key: string; reward: number; balance: number }>(
      `/players/${playerId}/achievements/${key}/claim`,
      { method: "POST" },
    ),
};
