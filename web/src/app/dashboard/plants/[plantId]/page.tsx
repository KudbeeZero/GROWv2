"use client";

import { use } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { RequireAuth } from "@/components/layout/RequireAuth";
import { Card, CardHeader } from "@/components/ui/Card";
import { LoadingBlock } from "@/components/ui/Spinner";
import { PlantVisual } from "@/components/plant/PlantVisual";
import { StatBars } from "@/components/plant/StatBars";
import { ConditionBadges } from "@/components/plant/ConditionBadges";
import { CareButtons } from "@/components/plant/CareButtons";
import { EventLog } from "@/components/plant/EventLog";
import { usePlantState } from "@/hooks/usePlantState";
import { useStrainMap } from "@/hooks/queries";
import { useSession } from "@/lib/session";
import { api } from "@/lib/api";
import { queryKeys } from "@/lib/queryKeys";
import { titleCase, num, dateTime } from "@/lib/format";

function PlantDetail({ plantId }: { plantId: string }) {
  const { playerId } = useSession();
  const { data: plant, isLoading, isError, error } = usePlantState(playerId!, plantId);
  const { map } = useStrainMap();
  const events = useQuery({
    queryKey: queryKeys.events(plantId),
    queryFn: () => api.plants.events(plantId, 50),
    refetchInterval: 10_000,
  });

  if (isLoading) return <LoadingBlock label="Loading plant…" />;
  if (isError || !plant)
    return (
      <Card>
        <p className="text-sm text-gray-300">Couldn&apos;t load plant: {error?.message}</p>
        <Link href="/dashboard" className="text-sm text-grow-300">
          ← Back to dashboard
        </Link>
      </Card>
    );

  const strain = map.get(plant.strain_id);

  return (
    <div className="space-y-4">
      <Link href="/dashboard" className="text-sm text-grow-300 hover:underline">
        ← Back to dashboard
      </Link>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader
            title={strain?.name ?? "Plant"}
            subtitle={`${titleCase(plant.growth_stage)} · ${num(plant.height, 1)} cm`}
          />
          <div className="flex items-center justify-center rounded-lg bg-ink-900/60 py-4">
            <PlantVisual stage={plant.growth_stage} flags={plant.condition_flags} size={200} />
          </div>
          <div className="mt-3">
            <ConditionBadges flags={plant.condition_flags} />
          </div>
        </Card>

        <Card className="lg:col-span-2 space-y-4">
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-300">Vitals</h3>
            <StatBars plant={plant} />
          </div>
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-300">Care</h3>
            <CareButtons plant={plant} />
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
            <span>Planted: {dateTime(plant.planted_at)}</span>
            <span>Alive: {plant.is_alive ? "yes" : "no"}</span>
            <span>Pod: {plant.pod_id.slice(0, 8)}…</span>
            <span>Plant ID: {plant.id.slice(0, 8)}…</span>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader title="Event log" subtitle="Stage changes, stress onsets and care actions" />
        {events.isLoading ? (
          <LoadingBlock />
        ) : (
          <EventLog events={events.data ?? plant.recent_events} />
        )}
      </Card>
    </div>
  );
}

export default function PlantPage({ params }: { params: Promise<{ plantId: string }> }) {
  const { plantId } = use(params);
  return (
    <RequireAuth>
      <PlantDetail plantId={plantId} />
    </RequireAuth>
  );
}
