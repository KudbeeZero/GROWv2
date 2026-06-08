"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/session";
import { OnboardingPanel } from "@/components/onboarding/OnboardingPanel";
import { Constellation } from "@/components/viz/Constellation";

export default function OnboardingPage() {
  const { isAuthed, hydrated } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (hydrated && isAuthed) router.replace("/dashboard");
  }, [hydrated, isAuthed, router]);

  return (
    <div className="grid items-center gap-8 py-6 lg:grid-cols-2">
      <div>
        <Constellation
          mode="leaf"
          height={420}
          leafCount={620}
          caption="DRAG · SCROLL · LIVE PARTICLES"
        />
        <div className="mt-5">
          <div className="instrument-label mb-1">GALACTIC SERIES · GROWPOD EMPIRE</div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-50">
            Real genetics. Real time.{" "}
            <span className="text-glow-grow text-grow-300">Provably yours.</span>
          </h1>
          <p className="mt-2 max-w-md text-sm text-gray-400">
            Cultivate a living simulation, breed discovered cultivars, and register them on a
            verifiable family tree. A genome is a graph — so we render it as one.
          </p>
        </div>
      </div>
      <div className="lg:pl-6">
        <OnboardingPanel />
      </div>
    </div>
  );
}
