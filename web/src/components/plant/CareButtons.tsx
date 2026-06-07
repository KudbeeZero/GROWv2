"use client";

import { Button } from "@/components/ui/Button";
import { useCareActions } from "@/hooks/useCareActions";
import type { PlantState } from "@/lib/types";

export function CareButtons({ plant }: { plant: PlantState }) {
  const { care, harvest } = useCareActions(plant.id);
  const disabled = !plant.is_alive || plant.harvested;
  const canHarvest = plant.growth_stage === "harvest" && !plant.harvested && plant.is_alive;
  const pending = care.isPending ? care.variables : null;

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        size="sm"
        variant="secondary"
        disabled={disabled}
        loading={pending === "water"}
        onClick={() => care.mutate("water")}
      >
        💧 Water
      </Button>
      <Button
        size="sm"
        variant="secondary"
        disabled={disabled}
        loading={pending === "feed"}
        onClick={() => care.mutate("feed")}
      >
        🧪 Feed
      </Button>
      <Button
        size="sm"
        variant="secondary"
        disabled={disabled || plant.pest_level <= 0}
        loading={pending === "treatPests"}
        onClick={() => care.mutate("treatPests")}
      >
        🐞 Treat Pests
      </Button>
      <Button
        size="sm"
        variant="secondary"
        disabled={disabled || plant.disease_level <= 0}
        loading={pending === "treatDisease"}
        onClick={() => care.mutate("treatDisease")}
      >
        🧫 Treat Disease
      </Button>
      {canHarvest && (
        <Button
          size="sm"
          variant="primary"
          loading={harvest.isPending}
          onClick={() => harvest.mutate({ sell: true })}
        >
          ✂️ Harvest & Sell
        </Button>
      )}
    </div>
  );
}
