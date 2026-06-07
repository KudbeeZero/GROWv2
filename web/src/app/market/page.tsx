"use client";

import { RequireAuth } from "@/components/layout/RequireAuth";
import { Card, CardHeader } from "@/components/ui/Card";
import { LoadingBlock } from "@/components/ui/Spinner";
import { ListingCard } from "@/components/market/ListingCard";
import { CreateListingForm } from "@/components/market/CreateListingForm";
import { useMarket } from "@/hooks/queries";

function MarketInner() {
  const market = useMarket();
  const listings = market.data ?? [];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold">Marketplace</h1>
        <p className="text-sm text-gray-400">Trade seeds with other growers — fixed price or auction.</p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader title="Sell a seed" />
        <CreateListingForm />
      </Card>

      <div>
        <h2 className="mb-2 text-lg font-semibold">Active listings</h2>
        {market.isLoading ? (
          <LoadingBlock />
        ) : listings.length === 0 ? (
          <Card>
            <p className="text-sm text-gray-400">No active listings right now.</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {listings.map((l) => (
              <ListingCard key={l.id} listing={l} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function MarketPage() {
  return (
    <RequireAuth>
      <MarketInner />
    </RequireAuth>
  );
}
