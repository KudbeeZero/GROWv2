"use client";

import { useState } from "react";
import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { RequireAuth } from "@/components/layout/RequireAuth";
import { Card, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { LoadingBlock } from "@/components/ui/Spinner";
import { Field, Select, TextInput } from "@/components/ui/Field";
import { useToast } from "@/components/ui/Toast";
import { useStrains } from "@/hooks/queries";
import { api, ApiError } from "@/lib/api";
import { useSession } from "@/lib/session";
import { queryKeys } from "@/lib/queryKeys";
import { RARITY_STYLES, titleCase, num } from "@/lib/format";
import type { Strain } from "@/lib/types";

function BreedInner() {
  const { playerId } = useSession();
  const toast = useToast();
  const qc = useQueryClient();
  const strains = useStrains({});

  const [parentA, setParentA] = useState("");
  const [parentB, setParentB] = useState("");
  const [name, setName] = useState("");
  const [result, setResult] = useState<Strain | null>(null);

  const all = strains.data ?? [];
  const a = parentA || all[0]?.id || "";
  const b = parentB || all[1]?.id || "";
  const bred = all.filter((s) => !s.is_base_catalog);

  const breed = useMutation<Strain, ApiError>({
    mutationFn: () => api.breeding.breed(playerId!, a, b, { name: name || undefined }),
    onSuccess: (offspring) => {
      setResult(offspring);
      toast.success(`Bred "${offspring.name}"`);
      qc.invalidateQueries({ queryKey: ["strains"] });
      qc.invalidateQueries({ queryKey: queryKeys.seeds(playerId!) });
      qc.invalidateQueries({ queryKey: queryKeys.wallet(playerId!) });
    },
    onError: (e) => toast.error(e.message),
  });

  const stabilize = useMutation<Strain, ApiError, string>({
    mutationFn: (strainId) => api.strains.stabilize(playerId!, strainId),
    onSuccess: (s) => {
      toast.success(`Stabilized "${s.name}" → ${Math.round(s.stability * 100)}%`);
      qc.invalidateQueries({ queryKey: ["strains"] });
    },
    onError: (e) => toast.error(e.message),
  });

  if (strains.isLoading) return <LoadingBlock label="Loading strains…" />;

  return (
    <div className="space-y-5">
      <Link href="/lab" className="text-sm text-grow-300 hover:underline">
        ← Back to Strain Lab
      </Link>
      <h1 className="text-2xl font-bold">Breeding & Stabilization</h1>

      <Card>
        <CardHeader
          title="Cross two parents"
          subtitle="Offspring inherit blended traits; fresh crosses lose stability until stabilized."
        />
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <Field label="Parent A">
            <Select value={a} onChange={(e) => setParentA(e.target.value)}>
              {all.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.rarity})
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Parent B">
            <Select value={b} onChange={(e) => setParentB(e.target.value)}>
              {all.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.rarity})
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Offspring name (optional)">
            <TextInput value={name} onChange={(e) => setName(e.target.value)} placeholder="Auto" />
          </Field>
        </div>
        <div className="mt-3">
          <Button
            loading={breed.isPending}
            disabled={a === b}
            onClick={() => breed.mutate()}
          >
            🧬 Breed (fee applies)
          </Button>
          {a === b && <span className="ml-2 text-xs text-amber-400">Pick two different parents.</span>}
        </div>

        {result && (
          <div className="mt-4 rounded-lg border border-grow-700 bg-grow-900/30 p-3">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-grow-200">{result.name}</span>
              <Badge className={RARITY_STYLES[result.rarity]}>{titleCase(result.rarity)}</Badge>
              <span className="text-xs text-gray-400">Gen {result.generation}</span>
            </div>
            <div className="mt-1 text-xs text-gray-400">
              THC {num(result.thc_range[0], 1)}–{num(result.thc_range[1], 1)}% · Stability{" "}
              {Math.round(result.stability * 100)}% · A seed was added to your inventory.
            </div>
          </div>
        )}
      </Card>

      <Card>
        <CardHeader
          title="Stabilize a bred strain"
          subtitle="Raise stability toward true-breeding so it can be minted as an NFT."
        />
        {bred.length === 0 ? (
          <p className="text-sm text-gray-500">No bred strains yet — cross two parents above first.</p>
        ) : (
          <ul className="space-y-2">
            {bred.map((s) => (
              <li
                key={s.id}
                className="flex items-center justify-between gap-2 rounded-md border border-ink-700 bg-ink-900/50 px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-200">{s.name}</span>
                  <Badge className={RARITY_STYLES[s.rarity]}>{titleCase(s.rarity)}</Badge>
                  <span className="text-xs text-gray-500">
                    stability {Math.round(s.stability * 100)}%
                  </span>
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  loading={stabilize.isPending && stabilize.variables === s.id}
                  onClick={() => stabilize.mutate(s.id)}
                >
                  Stabilize
                </Button>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

export default function BreedPage() {
  return (
    <RequireAuth>
      <BreedInner />
    </RequireAuth>
  );
}
