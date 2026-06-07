// Hand-written types mirroring the backend serializers
// (src/growpodempire/api/serialize.py). The OpenAPI spec carries no body
// schemas, so these are the source of truth for the wire format on the client.

export type GrowthStage =
  | "seed"
  | "germination"
  | "seedling"
  | "vegetative"
  | "flowering"
  | "harvest";

export type Rarity = "common" | "uncommon" | "rare" | "epic" | "legendary";

export type LineageType = "landrace" | "hybrid" | "bred";

export type ConditionKind =
  | "healthy"
  | "overwatered"
  | "root_rot"
  | "underwatered"
  | "wilting"
  | "nutrient_deficient"
  | "nutrient_burn"
  | "pest_infestation"
  | "mildew"
  | "dead";

export type Severity = "mild" | "moderate" | "severe";

export type NftStatus = "none" | "pending" | "minted" | "failed";

export interface ConditionFlag {
  condition: ConditionKind;
  severity: Severity;
}

export interface Wallet {
  id: string;
  player_id: string;
  balance: number;
  asa_balance: number | null;
  version: number;
}

export interface Player {
  id: string;
  username: string;
  email: string | null;
  algorand_address: string | null;
  xp: number;
  level: number;
  created_at: string | null;
  balance?: number;
  wallet?: Wallet;
  /** Returned exactly once, on player creation. */
  api_key?: string;
}

export interface LevelProgress {
  xp: number;
  level: number;
  xp_into_level: number;
  xp_for_next_level: number;
  progress_pct: number;
}

export interface Strain {
  id: string;
  name: string;
  slug: string;
  lineage_type: LineageType;
  rarity: Rarity;
  indica_ratio: number;
  thc_range: [number, number];
  cbd_range: [number, number];
  flowering_days: [number, number];
  yield_range: [number, number];
  difficulty: number;
  terpenes: string[] | null;
  stability: number;
  generation: number;
  parent_a_id: string | null;
  parent_b_id: string | null;
  is_base_catalog: boolean;
  genome: Record<string, { value: number; dominance: string }> | null;
  nft_asset_id: number | null;
  nft_status: NftStatus;
}

export type SeedSource = "starter" | "purchased" | "bred" | "market";

export interface Seed {
  id: string;
  strain_id: string;
  quantity: number;
  source: SeedSource;
  feminized: boolean;
}

export type PodTier = "basic" | "standard" | "pro";

export interface Pod {
  id: string;
  player_id: string;
  name: string;
  capacity: number;
  tier: PodTier;
  active: boolean;
  auto_water: boolean;
  auto_feed: boolean;
}

export interface Plant {
  id: string;
  player_id: string;
  pod_id: string;
  strain_id: string;
  growth_stage: GrowthStage;
  planted_at: string | null;
  height: number;
  health: number;
  water_level: number;
  nutrient_level: number;
  pest_level: number;
  disease_level: number;
  condition_flags: ConditionFlag[];
  is_alive: boolean;
  harvested: boolean;
}

export interface PlantEvent {
  id: string;
  plant_id: string;
  timestamp: string | null;
  event_type: string;
  severity: Severity | null;
  payload: Record<string, unknown> | null;
}

export interface PlantState extends Plant {
  recent_events: PlantEvent[];
}

export interface Harvest {
  id: string;
  player_id: string;
  plant_id: string;
  strain_id: string;
  weight_g: number;
  quality: number;
  thc_actual: number | null;
  cbd_actual: number | null;
  rarity: Rarity;
  sale_value: number | null;
  sold: boolean;
  harvested_at: string | null;
  nft_asset_id: number | null;
  nft_status: NftStatus;
}

export type ListingItemType = "seed" | "harvest";
export type ListingStatus = "active" | "sold" | "cancelled" | "expired";

export interface Listing {
  id: string;
  seller_id: string;
  item_type: ListingItemType;
  item_ref_id: string;
  quantity: number;
  unit_price: number;
  status: ListingStatus;
  buyer_id: string | null;
  is_auction: boolean;
  min_bid: number | null;
  highest_bid: number | null;
  highest_bidder_id: string | null;
  expires_at: string | null;
}

export interface Contract {
  id: string;
  description: string;
  target_rarity: Rarity | null;
  target_grams: number;
  reward_grow: number;
  reward_xp: number;
  status: "open" | "fulfilled" | "expired";
  deadline_at: string | null;
  fulfilled_at: string | null;
}

export interface LedgerEntry {
  id: string;
  entry_type: string;
  amount: number;
  balance_after: number;
  ref_type: string | null;
  ref_id: string | null;
  created_at: string | null;
}

export interface Achievement {
  key: string;
  description: string;
  reward: number;
  unlocked: boolean;
  claimed: boolean;
}

export interface LeaderboardEntry {
  player_id: string;
  username: string;
  value: number;
}

export type LeaderboardKind = "richest" | "breeders" | "harvests" | "level";

/** Error body shape returned by the API on failures. */
export interface ApiErrorBody {
  error: string;
}
