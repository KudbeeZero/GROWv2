"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { StrainFilters } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import { useSession } from "@/lib/session";
import type { LeaderboardKind } from "@/lib/types";

export function usePlayer() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.player(playerId ?? ""),
    queryFn: () => api.players.get(playerId!),
    enabled: isAuthed,
  });
}

export function useWallet() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.wallet(playerId ?? ""),
    queryFn: () => api.players.wallet(playerId!),
    enabled: isAuthed,
  });
}

export function useLevel() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.level(playerId ?? ""),
    queryFn: () => api.players.level(playerId!),
    enabled: isAuthed,
  });
}

export function useLedger() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.ledger(playerId ?? ""),
    queryFn: () => api.players.ledger(playerId!),
    enabled: isAuthed,
  });
}

export function useAchievements() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.achievements(playerId ?? ""),
    queryFn: () => api.players.achievements(playerId!),
    enabled: isAuthed,
  });
}

export function useSeeds() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.seeds(playerId ?? ""),
    queryFn: () => api.seeds.list(playerId!),
    enabled: isAuthed,
  });
}

export function usePods() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.pods(playerId ?? ""),
    queryFn: () => api.pods.list(playerId!),
    enabled: isAuthed,
  });
}

export function usePlantsList() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.plants(playerId ?? ""),
    queryFn: () => api.plants.list(playerId!),
    enabled: isAuthed,
  });
}

export function useStrains(filters: StrainFilters) {
  return useQuery({
    queryKey: queryKeys.strains(filters),
    queryFn: () => api.strains.list(filters),
  });
}

/** All strains as an id -> Strain map, for name/rarity lookups across the app. */
export function useStrainMap() {
  const q = useQuery({
    queryKey: queryKeys.strains({}),
    queryFn: () => api.strains.list({}),
    staleTime: 60_000,
  });
  const map = new Map((q.data ?? []).map((s) => [s.id, s]));
  return { map, ...q };
}

export function useFavorites() {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.favorites(playerId ?? ""),
    queryFn: () => api.strains.favorites(playerId!),
    enabled: isAuthed,
  });
}

export function useMarket() {
  return useQuery({
    queryKey: queryKeys.market(),
    queryFn: () => api.market.list(),
    refetchInterval: 15_000,
  });
}

export function useContracts(status?: "open" | "fulfilled") {
  const { playerId, isAuthed } = useSession();
  return useQuery({
    queryKey: queryKeys.contracts(playerId ?? "", status),
    queryFn: () => api.contracts.list(playerId!, status),
    enabled: isAuthed,
  });
}

export function useLeaderboard(board: LeaderboardKind) {
  return useQuery({
    queryKey: queryKeys.leaderboard(board),
    queryFn: () => api.leaderboards.get(board),
  });
}
