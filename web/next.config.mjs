/** @type {import('next').NextConfig} */

// The API base the browser is allowed to call (XHR/fetch). Mirrors
// NEXT_PUBLIC_API_BASE so the Content-Security-Policy connect-src stays in sync.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:10000";

// Defence-in-depth HTTP security headers.
//
// CSP note: the App Router emits inline bootstrap/hydration scripts. The only
// ways to allow them are a per-request nonce (which can't be baked into the
// statically-prerendered pages this app ships) or 'unsafe-inline'. We take
// 'unsafe-inline' — the same posture already used for styles. Script *sources*
// are still locked to same-origin (no attacker-hosted scripts) and eval is
// disallowed, so this keeps meaningful XSS mitigation while letting the app
// actually hydrate. connect-src is limited to self + the configured API origin.
const csp = [
  "default-src 'self'",
  "base-uri 'self'",
  "frame-ancestors 'none'",
  "object-src 'none'",
  "img-src 'self' data: blob:",
  "style-src 'self' 'unsafe-inline'",
  "script-src 'self' 'unsafe-inline'",
  "font-src 'self' data:",
  `connect-src 'self' ${API_BASE}`,
  "form-action 'self'",
].join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: csp },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains; preload",
  },
];

const nextConfig = {
  reactStrictMode: true,
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
};

export default nextConfig;
