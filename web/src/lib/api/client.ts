// Typed fetch wrapper around the GROWv2 game API.
//
// - Resolves the base URL from NEXT_PUBLIC_API_BASE and prefixes /api/game.
// - Injects the X-API-Key header (read from localStorage) on write requests.
// - Normalizes the backend's {error} body into a thrown ApiError.

import type { ApiErrorBody } from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://localhost:10000";

const GAME_PREFIX = "/api/game";

export const API_KEY_STORAGE = "gpe.api_key";
export const PLAYER_ID_STORAGE = "gpe.player_id";

export class ApiError extends Error {
  status: number;
  body: ApiErrorBody | null;
  constructor(message: string, status: number, body: ApiErrorBody | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function readApiKey(): string | null {
  if (typeof window === "undefined") return null;
  // localStorage can throw (privacy mode, disabled storage, quota); never let
  // that turn into an opaque request failure.
  try {
    return window.localStorage.getItem(API_KEY_STORAGE);
  } catch {
    return null;
  }
}

type Method = "GET" | "POST" | "PUT" | "DELETE";

interface FetchOptions {
  method?: Method;
  body?: unknown;
  /** Send the X-API-Key header. Defaults to true for writes, false for GET. */
  auth?: boolean;
  /** Treat `path` as an absolute path under the API host (skip /api/game). */
  raw?: boolean;
  query?: Record<string, string | number | boolean | null | undefined>;
}

function buildUrl(path: string, raw: boolean, query?: FetchOptions["query"]): string {
  const prefix = raw ? "" : GAME_PREFIX;
  const url = new URL(`${API_BASE}${prefix}${path}`);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

export async function apiFetch<T>(path: string, opts: FetchOptions = {}): Promise<T> {
  const method = opts.method ?? "GET";
  const isWrite = method !== "GET";
  const auth = opts.auth ?? isWrite;

  const headers: Record<string, string> = {};
  if (opts.body !== undefined) headers["Content-Type"] = "application/json";

  if (auth) {
    const key = readApiKey();
    if (!key) {
      throw new ApiError("Not authenticated — create or import a player first", 401);
    }
    headers["X-API-Key"] = key;
  }

  let res: Response;
  try {
    res = await fetch(buildUrl(path, opts.raw ?? false, opts.query), {
      method,
      headers,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    });
  } catch {
    throw new ApiError("Network error — is the API running?", 0);
  }

  const text = await res.text();
  let data: unknown = undefined;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const body = (data ?? null) as ApiErrorBody | null;
    const message =
      body && typeof body === "object" && "error" in body
        ? String(body.error)
        : `Request failed (${res.status})`;
    throw new ApiError(message, res.status, body);
  }

  return data as T;
}
