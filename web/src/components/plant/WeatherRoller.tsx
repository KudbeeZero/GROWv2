"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import { useSession } from "@/lib/session";
import { useToast } from "@/components/ui/Toast";
import { Button } from "@/components/ui/Button";
import { titleCase } from "@/lib/format";

const EVENTS = ["heatwave", "cold_snap", "humidity_spike", "pest_swarm", "ideal"];

export function WeatherRoller({ podId }: { podId: string }) {
  const { playerId } = useSession();
  const toast = useToast();
  const qc = useQueryClient();

  const roll = useMutation<Record<string, unknown>, ApiError, string | undefined>({
    mutationFn: (event) => api.pods.rollWeather(playerId!, podId, event),
    onSuccess: (res) => {
      const ev = (res["event"] ?? res["weather"] ?? "weather") as string;
      toast.push(`Weather: ${titleCase(String(ev))}`, "info");
      qc.invalidateQueries({ queryKey: ["plant"] });
    },
    onError: (e) => toast.error(e.message),
  });

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Button size="sm" variant="secondary" loading={roll.isPending} onClick={() => roll.mutate(undefined)}>
        🎲 Random Weather
      </Button>
      {EVENTS.map((ev) => (
        <Button
          key={ev}
          size="sm"
          variant="ghost"
          disabled={roll.isPending}
          onClick={() => roll.mutate(ev)}
        >
          {titleCase(ev)}
        </Button>
      ))}
    </div>
  );
}
