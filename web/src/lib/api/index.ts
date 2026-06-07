import { players } from "./players";
import { strains } from "./strains";
import { seeds } from "./seeds";
import { pods } from "./pods";
import { plants } from "./plants";
import { breeding } from "./breeding";
import { market } from "./market";
import { contracts } from "./contracts";
import { leaderboards } from "./leaderboards";
import { wallet } from "./wallet";

export const api = {
  players,
  strains,
  seeds,
  pods,
  plants,
  breeding,
  market,
  contracts,
  leaderboards,
  wallet,
};

export { ApiError } from "./client";
export type { StrainFilters } from "./strains";
export type { Environment } from "./pods";
