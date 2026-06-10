// Visual QA for the rebuilt PlantVisual: screenshot the plant SVG at each
// growth stage. Run from web/: node capture-new-render.mjs <playerId> <apiKey> <plantId>
import { chromium } from "@playwright/test";
import { execSync } from "node:child_process";
import { mkdirSync } from "node:fs";

const [playerId, apiKey, plantId] = process.argv.slice(2);
const OUT = "/home/user/GROWv2/artifacts/new-render";
mkdirSync(OUT, { recursive: true });

// stage, variant, filename
const SHOTS = [
  ["seedling", "", "seedling"],
  ["vegetative", "", "vegetative"],
  ["flowering", "", "flowering"],
  ["harvest", "", "harvest"],
];

const ENV = {
  ...process.env,
  PYTHONPATH: "src",
  DATABASE_URL: "sqlite:////tmp/newrender.db",
  USE_MOCK_AI: "true",
  USE_MOCK_CHAIN: "true",
};

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const page = await ctx.newPage();
const errors = [];
page.on("console", (m) => {
  if (m.type() === "error") errors.push(m.text());
});
page.on("pageerror", (e) => errors.push("PAGEERROR: " + e.message));

await page.addInitScript(
  ({ playerId, apiKey }) => {
    localStorage.setItem("gpe.player_id", playerId);
    localStorage.setItem("gpe.api_key", apiKey);
  },
  { playerId, apiKey },
);

const url = `http://localhost:3000/dashboard/plants/${plantId}`;

for (const [stage, variant, name] of SHOTS) {
  execSync(`python /tmp/set_stage.py ${plantId} ${stage} ${variant}`, {
    cwd: "/home/user/GROWv2",
    env: ENV,
    stdio: "inherit",
  });

  await page.goto(url, { waitUntil: "domcontentloaded" });
  await page
    .waitForFunction(
      () => !document.body.textContent?.includes("Loading session"),
      { timeout: 30_000 },
    )
    .catch(() => console.log(`  [warn] still loading session for ${name}`));
  await page
    .waitForSelector('svg[role="img"]', { timeout: 20_000 })
    .catch(() => console.log(`  [warn] no svg for ${name}`));
  await page.waitForTimeout(1200);

  // Tight crop of just the plant visual SVG.
  const svg = page.locator('svg[role="img"]').first();
  if (await svg.count()) {
    await svg
      .screenshot({ path: `${OUT}/${name}.png` })
      .catch((e) => console.log(`  [warn] svg crop failed ${name}: ${e.message}`));
  } else {
    console.log(`  [warn] no SVG to crop for ${name}`);
  }

  // For flowering, also grab the full detail page.
  if (name === "flowering") {
    await page.screenshot({ path: `${OUT}/flowering-page.png`, fullPage: true });
  }

  const label = await svg.getAttribute("aria-label").catch(() => null);
  console.log(`captured ${name}: aria-label="${label}"`);
}

await browser.close();
if (errors.length) {
  console.log("\n=== CONSOLE/PAGE ERRORS ===");
  for (const e of [...new Set(errors)]) console.log(e);
} else {
  console.log("\nNo console errors.");
}
