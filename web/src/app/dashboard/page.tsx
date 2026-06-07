"use client";

import { useState } from "react";
import Link from "next/link";
import { RequireAuth } from "@/components/layout/RequireAuth";
import { Card, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingBlock } from "@/components/ui/Spinner";
import { CreatePodForm } from "@/components/pod/CreatePodForm";
import { PodCard } from "@/components/pod/PodCard";
import { PlantCard } from "@/components/plant/PlantCard";
import { ImportEntityForm } from "@/components/onboarding/ImportEntityForm";
import { usePods, usePlantsList } from "@/hooks/queries";
import { useSession } from "@/lib/session";
import { useIdStore } from "@/lib/localStore";

function DashboardInner() {
  const { playerId } = useSession();
  const pods = usePods();
  const plants = usePlantsList();
  const localPlantIds = useIdStore((s) => (playerId ? s.plantIds(playerId) : []));
  const [showCreate, setShowCreate] = useState(false);

  if (pods.isLoading) return <LoadingBlock label="Loading your grow…" />;

  const podList = pods.data ?? [];

  // Group plant ids by pod, merging the authoritative list with any local ids.
  const byPod = new Map<string, string[]>();
  for (const p of plants.data ?? []) {
    const arr = byPod.get(p.pod_id) ?? [];
    arr.push(p.id);
    byPod.set(p.pod_id, arr);
  }
  const knownIds = new Set((plants.data ?? []).map((p) => p.id));
  const orphanLocal = localPlantIds.filter((id) => !knownIds.has(id));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Grow Dashboard</h1>
          <p className="text-sm text-gray-400">
            Plants advance in real time as you watch — care for them before they wilt.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/lab">
            <Button variant="secondary" size="sm">
              Buy seeds
            </Button>
          </Link>
          <Button size="sm" onClick={() => setShowCreate((s) => !s)}>
            + New Pod
          </Button>
        </div>
      </div>

      {showCreate && (
        <Card className="max-w-md">
          <CardHeader title="Create a grow pod" />
          <CreatePodForm onCreated={() => setShowCreate(false)} />
        </Card>
      )}

      {podList.length === 0 ? (
        <Card>
          <p className="text-sm text-gray-300">
            You don&apos;t have any pods yet. Create one to start growing.
          </p>
        </Card>
      ) : (
        <div className="space-y-6">
          {podList.map((pod) => {
            const ids = byPod.get(pod.id) ?? [];
            // include local ids whose pod we don't yet know on the first one
            return <PodCard key={pod.id} pod={pod} plantIds={ids} />;
          })}
        </div>
      )}

      {orphanLocal.length > 0 && (
        <Card>
          <CardHeader
            title="Other tracked plants"
            subtitle="Plants saved locally but not in a loaded pod."
          />
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {/* Rendered without pod context; PlantCard fetches its own state */}
            {orphanLocal.map((id) => (
              <OrphanPlant key={id} playerId={playerId!} plantId={id} />
            ))}
          </div>
        </Card>
      )}

      <Card>
        <CardHeader
          title="Recover a plant"
          subtitle="Switched devices or cleared storage? Import a plant by its ID."
        />
        <ImportEntityForm />
      </Card>
    </div>
  );
}

function OrphanPlant({ playerId, plantId }: { playerId: string; plantId: string }) {
  return <PlantCard playerId={playerId} plantId={plantId} />;
}

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardInner />
    </RequireAuth>
  );
}
