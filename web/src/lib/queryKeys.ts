import type { LeaderboardKind } from "@/lib/types";
import type { StrainFilters } from "@/lib/api";

export const queryKeys = {
  player: (id: string) => ["player", id] as const,
  wallet: (id: string) => ["wallet", id] as const,
  level: (id: string) => ["level", id] as const,
  ledger: (id: string) => ["ledger", id] as const,
  achievements: (id: string) => ["achievements", id] as const,
  strains: (filters: StrainFilters) => ["strains", filters] as const,
  favorites: (id: string) => ["favorites", id] as const,
  seeds: (id: string) => ["seeds", id] as const,
  pods: (id: string) => ["pods", id] as const,
  plants: (id: string) => ["plants", id] as const,
  plant: (plantId: string) => ["plant", plantId] as const,
  events: (plantId: string) => ["events", plantId] as const,
  market: () => ["market"] as const,
  contracts: (id: string, status?: string) => ["contracts", id, status ?? "all"] as const,
  leaderboard: (board: LeaderboardKind) => ["leaderboard", board] as const,
};
