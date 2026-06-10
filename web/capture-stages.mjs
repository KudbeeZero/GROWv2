// Visual QA: screenshot the PlantVisual at each growth stage / condition variant.
// Run from web/: node capture-stages.mjs <playerId> <apiKey> <plantId>
import { chromium } from "@playwright/test";
import { execSync } from "node:child_process";
import { mkdirSync } from "node:fs";

const [playerId, apiKey, plantId] = process.argv.slice(2);
const OUT = "/home/user/GROWv2/artifacts/plant-stages";
mkdirSync(OUT, { recursive: true });

// stage, variant, filename
const SHOTS = [
  ["seed", "", "seed"],
  ["germination", "", "germination"],
  ["seedling", "", "seedling"],
  ["vegetative", "", "vegetative"],
  ["flowering", "", "flowering"],
  ["harvest", "", "harvest"],
  ["vegetative", "drooping", "condition-drooping"],
  ["vegetative", "pests", "condition-pests"],
  ["flowering", "mildew", "condition-mildew"],
];

const ENV = {
  ...process.env,
  PYTHONPATH: "src",
  DATABASE_URL: "sqlite:////tmp/visualqa.db",
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

// Seed localStorage before any script runs.
await page.addInitScript(
  ({ playerId, apiKey }) => {
    localStorage.setItem("gpe.player_id", playerId);
    localStorage.setItem("gpe.api_key", apiKey);
  },
  { playerId, apiKey },
);

const url = `http://localhost:3000/dashboard/plants/${plantId}`;

for (const [stage, variant, name] of SHOTS) {
  // Mutate DB state for this stage from the backend repo dir.
  execSync(`python /tmp/set_stage.py ${plantId} ${stage} ${variant}`, {
    cwd: "/home/user/GROWv2",
    env: ENV,
    stdio: "inherit",
  });

  await page.goto(url, { waitUntil: "domcontentloaded" });
  // Wait for RequireAuth to finish hydrating (spinner text disappears).
  await page
    .waitForFunction(
      () => !document.body.textContent?.includes("Loading session"),
      { timeout: 30_000 },
    )
    .catch(() => console.log(`  [warn] still loading session for ${name}`));
  // Wait for the plant visual SVG (role=img) to render.
  await page
    .waitForSelector('svg[role="img"]', { timeout: 20_000 })
    .catch(() => console.log(`  [warn] no svg for ${name}`));
  await page.waitForTimeout(1000); // let react-query settle + CSS anim frame

  // Full plant detail page shot.
  await page.screenshot({ path: `${OUT}/${name}-page.png` });

  // Tight crop of just the plant visual SVG.
  const svg = page.locator('svg[role="img"]').first();
  if (await svg.count()) {
    await svg
      .screenshot({ path: `${OUT}/${name}.png` })
      .catch((e) => console.log(`  [warn] svg crop failed ${name}: ${e.message}`));
  } else {
    console.log(`  [warn] no SVG to crop for ${name}`);
  }

  const label = await svg.getAttribute("aria-label").catch(() => null);
  const heading = await page
    .locator("text=/cm/")
    .first()
    .textContent()
    .catch(() => null);
  console.log(`captured ${name}: aria-label="${label}" subtitle="${heading}"`);
}

await browser.close();
if (errors.length) {
  console.log("\n=== CONSOLE/PAGE ERRORS ===");
  for (const e of [...new Set(errors)]) console.log(e);
} else {
  console.log("\nNo console errors.");
}
