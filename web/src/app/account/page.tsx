"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { RequireAuth } from "@/components/layout/RequireAuth";
import { Card, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Bar } from "@/components/ui/Bar";
import { LoadingBlock } from "@/components/ui/Spinner";
import { useToast } from "@/components/ui/Toast";
import {
  usePlayer,
  useWallet,
  useLevel,
  useAchievements,
  useLedger,
} from "@/hooks/queries";
import { api, ApiError } from "@/lib/api";
import { useSession } from "@/lib/session";
import { queryKeys } from "@/lib/queryKeys";
import { grow, dateTime, titleCase } from "@/lib/format";

function AccountInner() {
  const { playerId, logout } = useSession();
  const player = usePlayer();
  const wallet = useWallet();
  const level = useLevel();
  const achievements = useAchievements();
  const ledger = useLedger();
  const toast = useToast();
  const qc = useQueryClient();

  const daily = useMutation<{ amount: number; balance: number }, ApiError>({
    mutationFn: () => api.players.claimDaily(playerId!),
    onSuccess: (r) => {
      toast.success(`Claimed ${grow(r.amount)} daily stipend`);
      refreshMoney();
    },
    onError: (e) => toast.error(e.message),
  });

  const claim = useMutation<unknown, ApiError, string>({
    mutationFn: (key) => api.players.claimAchievement(playerId!, key),
    onSuccess: () => {
      toast.success("Achievement reward claimed");
      qc.invalidateQueries({ queryKey: queryKeys.achievements(playerId!) });
      refreshMoney();
    },
    onError: (e) => toast.error(e.message),
  });

  function refreshMoney() {
    qc.invalidateQueries({ queryKey: queryKeys.wallet(playerId!) });
    qc.invalidateQueries({ queryKey: queryKeys.player(playerId!) });
    qc.invalidateQueries({ queryKey: queryKeys.ledger(playerId!) });
  }

  if (player.isLoading) return <LoadingBlock label="Loading account…" />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Account</h1>
        <Button variant="ghost" size="sm" onClick={logout}>
          Sign out
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardHeader title={player.data?.username} subtitle={player.data?.email ?? "no email"} />
          <div className="space-y-3">
            <div className="text-3xl font-bold text-grow-300">
              {grow(wallet.data?.balance)}
            </div>
            {level.data && (
              <div>
                <div className="mb-1 flex justify-between text-xs text-gray-400">
                  <span>Level {level.data.level}</span>
                  <span>{level.data.xp} XP · {level.data.xp_for_next_level} to next</span>
                </div>
                <Bar label="" value={level.data.progress_pct} color="bg-grow-500" />
              </div>
            )}
            <Button onClick={() => daily.mutate()} loading={daily.isPending}>
              Claim daily stipend
            </Button>
          </div>
        </Card>

        <Card>
          <CardHeader title="Achievements" />
          {achievements.isLoading ? (
            <LoadingBlock />
          ) : (
            <ul className="space-y-2">
              {(achievements.data ?? []).map((a) => (
                <li
                  key={a.key}
                  className="flex items-center justify-between gap-2 rounded-md border border-ink-700 bg-ink-900/50 px-3 py-2"
                >
                  <div>
                    <div className="text-sm font-medium text-gray-200">
                      {titleCase(a.key)}
                    </div>
                    <div className="text-xs text-gray-500">{a.description}</div>
                  </div>
                  {a.claimed ? (
                    <Badge className="border-ink-600 bg-ink-700 text-gray-400">Claimed</Badge>
                  ) : a.unlocked ? (
                    <Button size="sm" loading={claim.isPending} onClick={() => claim.mutate(a.key)}>
                      Claim {grow(a.reward)}
                    </Button>
                  ) : (
                    <Badge className="border-ink-700 bg-ink-800 text-gray-500">Locked</Badge>
                  )}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card>
        <CardHeader title="Ledger" subtitle="Every GROW movement, newest first" />
        {ledger.isLoading ? (
          <LoadingBlock />
        ) : (
          <div className="max-h-80 overflow-y-auto">
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 bg-ink-800 text-gray-400">
                <tr>
                  <th className="py-1 pr-2">When</th>
                  <th className="py-1 pr-2">Type</th>
                  <th className="py-1 pr-2 text-right">Amount</th>
                  <th className="py-1 text-right">Balance</th>
                </tr>
              </thead>
              <tbody>
                {(ledger.data ?? []).map((e) => (
                  <tr key={e.id} className="border-t border-ink-700">
                    <td className="py-1 pr-2 text-gray-500">{dateTime(e.created_at)}</td>
                    <td className="py-1 pr-2 text-gray-300">{titleCase(e.entry_type)}</td>
                    <td
                      className={`py-1 pr-2 text-right tabular-nums ${
                        e.amount >= 0 ? "text-grow-300" : "text-red-300"
                      }`}
                    >
                      {e.amount >= 0 ? "+" : ""}
                      {e.amount}
                    </td>
                    <td className="py-1 text-right tabular-nums text-gray-400">
                      {e.balance_after}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}

export default function AccountPage() {
  return (
    <RequireAuth>
      <AccountInner />
    </RequireAuth>
  );
}
