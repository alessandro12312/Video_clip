"use client";

import { Settings } from "lucide-react";
import { EmptyState } from "@/components/shared/empty-state";

export default function ImpostazioniPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Impostazioni account</h1>
      <EmptyState
        icon={Settings}
        title="In arrivo"
        description="Le impostazioni account saranno disponibili prossimamente."
      />
    </div>
  );
}
