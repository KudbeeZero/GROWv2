"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/lib/session";
import { OnboardingPanel } from "@/components/onboarding/OnboardingPanel";

export default function OnboardingPage() {
  const { isAuthed, hydrated } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (hydrated && isAuthed) router.replace("/dashboard");
  }, [hydrated, isAuthed, router]);

  return (
    <div className="py-10">
      <OnboardingPanel />
    </div>
  );
}
