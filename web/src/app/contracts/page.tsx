"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { RequireAuth } from "@/components/layout/RequireAuth";
import { Card, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { LoadingBlock } from "@/components/ui/Spinner";
import { useToast } from "@/components/ui/Toast";
import { useContracts } from "@/hooks/queries";
import { api, ApiError } from "@/lib/api";
import { useSession } from "@/lib/session";
import { queryKeys } from "@/lib/queryKeys";
import { grow, dateTime, titleCase, RARITY_STYLES } from "@/lib/format";

function ContractsInner() {
  const { playerId } = useSession();
  const toast = useToast();
  const qc = useQueryClient();
  const contracts = useContracts();

  function refresh() {
    qc.invalidateQueries({ queryKey: queryKeys.contracts(playerId!, undefined) });
    qc.invalidateQueries({ queryKey: queryKeys.wallet(playerId!) });
    qc.invalidateQueries({ queryKey: queryKeys.player(playerId!) });
  }

  const offer = useMutation<unknown, ApiError>({
    mutationFn: () => api.contracts.offer(playerId!),
    onSuccess: () => {
      toast.success("New contract offered");
      refresh();
    },
    onError: (e) => toast.error(e.message),
  });

  const fulfill = useMutation<unknown, ApiError, string>({
    mutationFn: (id) => api.contracts.fulfill(playerId!, id),
    onSuccess: () => {
      toast.success("Contract fulfilled — reward paid");
      refresh();
    },
    onError: (e) => toast.error(e.message),
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">NPC Contracts</h1>
          <p className="text-sm text-gray-400">Deliver harvests of a target rarity for GROW + XP.</p>
        </div>
        <Button onClick={() => offer.mutate()} loading={offer.isPending}>
          Request contract
        </Button>
      </div>

      {contracts.isLoading ? (
        <LoadingBlock />
      ) : (contracts.data ?? []).length === 0 ? (
        <Card>
          <p className="text-sm text-gray-400">No contracts yet — request one above.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {(contracts.data ?? []).map((c) => (
            <Card key={c.id}>
              <CardHeader
                title={c.description}
                action={
                  <Badge className="border-ink-600 bg-ink-700 text-gray-300">
                    {titleCase(c.status)}
                  </Badge>
                }
              />
              <div className="flex flex-wrap items-center gap-2 text-sm text-gray-300">
                {c.target_rarity && (
                  <Badge className={RARITY_STYLES[c.target_rarity]}>
                    {titleCase(c.target_rarity)}
                  </Badge>
                )}
                <span>{c.target_grams} g</span>
                <span className="text-grow-300">Reward {grow(c.reward_grow)}</span>
                <span className="text-gray-500">+{c.reward_xp} XP</span>
              </div>
              <div className="mt-1 text-xs text-gray-500">Deadline {dateTime(c.deadline_at)}</div>
              {c.status === "open" && (
                <Button
                  className="mt-3"
                  size="sm"
                  loading={fulfill.isPending && fulfill.variables === c.id}
                  onClick={() => fulfill.mutate(c.id)}
                >
                  Fulfill
                </Button>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ContractsPage() {
  return (
    <RequireAuth>
      <ContractsInner />
    </RequireAuth>
  );
}
