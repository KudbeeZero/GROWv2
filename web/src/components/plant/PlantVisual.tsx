"use client";

import type { CSSProperties } from "react";
import type { ConditionFlag, GrowthStage } from "@/lib/types";
import {
  CONDITION_VISUALS,
  SEVERITY_SCALE,
  dominantFlag,
  type Overlay,
} from "@/lib/conditionVisuals";

/* ---------------------------------------------------------------------------
 * A botanically-plausible cannabis plant, drawn as SVG.
 *
 * Building blocks:
 *  - A serrated palmate FAN LEAF (the iconic 7-leaflet marijuana leaf), defined
 *    once as <g id="cleaf"> and re-used at every node via <use>, rotated/scaled.
 *  - A central stalk with BRANCHING nodes; leaves come off the stalk (and, in
 *    flower, off branch tips) so the plant reads full, not hollow.
 *  - COLAS (bud clusters) that form at the crown + branch tips in flowering, and
 *    become fat, frosted (trichomes) and amber-pistilled at harvest.
 * Each growth stage has its own structure, so the silhouettes are all distinct.
 * ------------------------------------------------------------------------- */

// One unit leaflet ("blade"), petiole at (0,0), tip at (0,-1), serrated edges.
const BLADE =
  "M0,0 L0.05,-0.16 L0.10,-0.13 L0.12,-0.33 L0.16,-0.29 L0.12,-0.50 " +
  "L0.15,-0.48 L0.09,-0.70 L0.11,-0.68 L0.05,-0.87 L0,-1 " +
  "L-0.05,-0.87 L-0.11,-0.68 L-0.09,-0.70 L-0.15,-0.48 L-0.12,-0.50 " +
  "L-0.16,-0.29 L-0.12,-0.33 L-0.10,-0.13 L-0.05,-0.16 Z";

// The 7 leaflets of one fan leaf: {angle°, length-scale}. Centre longest.
const LEAFLETS = [
  { a: 0, s: 1 },
  { a: 24, s: 0.82 },
  { a: -24, s: 0.82 },
  { a: 50, s: 0.6 },
  { a: -50, s: 0.6 },
  { a: 76, s: 0.4 },
  { a: -76, s: 0.4 },
];

type Leaf = { x: number; y: number; angle: number; size: number };
type Branch = { x1: number; y1: number; x2: number; y2: number };
type Cola = { x: number; y: number; len: number; wid: number };

interface Plant {
  stemTop: number;
  branches: Branch[];
  leaves: Leaf[];
  colas: Cola[];
  frosted: boolean;
  sprout: boolean; // tiny seed/germination sprout instead of a full plant
}

// Layout per growth stage. `angle` = leaf rotation (0 = straight up, +right).
function buildPlant(stage: GrowthStage): Plant {
  switch (stage) {
    case "seed":
      return { stemTop: 99, branches: [], leaves: [], colas: [], frosted: false, sprout: true };
    case "germination":
      return {
        stemTop: 92,
        branches: [],
        leaves: [
          { x: 50, y: 93, angle: -40, size: 8 },
          { x: 50, y: 93, angle: 40, size: 8 },
        ],
        colas: [],
        frosted: false,
        sprout: true,
      };
    case "seedling":
      return {
        stemTop: 80,
        branches: [],
        leaves: [
          { x: 50, y: 95, angle: -62, size: 13 },
          { x: 50, y: 95, angle: 62, size: 13 },
          { x: 50, y: 84, angle: -40, size: 12 },
          { x: 50, y: 84, angle: 40, size: 12 },
          { x: 50, y: 80, angle: 0, size: 10 },
        ],
        colas: [],
        frosted: false,
        sprout: false,
      };
    default: {
      // vegetative / flowering / harvest share the bushy frame; flower/harvest add colas.
      const leaves: Leaf[] = [
        { x: 50, y: 97, angle: -80, size: 23 },
        { x: 50, y: 97, angle: 80, size: 23 },
        { x: 50, y: 86, angle: -62, size: 23 },
        { x: 50, y: 86, angle: 62, size: 23 },
        { x: 50, y: 75, angle: -47, size: 20 },
        { x: 50, y: 75, angle: 47, size: 20 },
        { x: 50, y: 64, angle: -33, size: 17 },
        { x: 50, y: 64, angle: 33, size: 17 },
        { x: 50, y: 55, angle: 0, size: 15 },
      ];
      const flowering = stage === "flowering" || stage === "harvest";
      const branches: Branch[] = flowering
        ? [
            { x1: 50, y1: 86, x2: 33, y2: 76 },
            { x1: 50, y1: 86, x2: 67, y2: 76 },
            { x1: 50, y1: 75, x2: 37, y2: 64 },
            { x1: 50, y1: 75, x2: 63, y2: 64 },
          ]
        : [];
      const colas: Cola[] = flowering
        ? [
            { x: 50, y: 52, len: 20, wid: 8 }, // apical cola (crown)
            { x: 33, y: 74, len: 12, wid: 6 }, // branch-tip colas
            { x: 67, y: 74, len: 12, wid: 6 },
            { x: 37, y: 62, len: 10, wid: 5 },
            { x: 63, y: 62, len: 10, wid: 5 },
          ]
        : [];
      return {
        stemTop: 52,
        branches,
        leaves,
        colas,
        frosted: stage === "harvest",
        sprout: false,
      };
    }
  }
}

function Overlays({ overlay }: { overlay: Overlay }) {
  if (overlay === "bugs")
    return (
      <g className="gpe-bug" fill="#1a1a1a">
        {[
          [40, 70],
          [62, 58],
          [52, 80],
          [70, 74],
          [34, 60],
        ].map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r="2.4" />
        ))}
      </g>
    );
  if (overlay === "mildew")
    return (
      <g className="gpe-mildew" fill="#e8edf2">
        <circle cx="44" cy="62" r="5" opacity="0.7" />
        <circle cx="58" cy="54" r="6" opacity="0.6" />
        <circle cx="52" cy="72" r="7" opacity="0.5" />
        <circle cx="66" cy="66" r="4" opacity="0.6" />
      </g>
    );
  if (overlay === "water-sheen")
    return (
      <rect className="gpe-sheen" x="10" y="20" width="30" height="90" fill="url(#sheen)" opacity="0.5" />
    );
  if (overlay === "rot")
    return <ellipse cx="50" cy="104" rx="22" ry="6" fill="#3b2f23" opacity="0.8" />;
  return null;
}

// A cola = a tapering cluster of calyx bumps along the stem; frosted+pistilled at harvest.
function ColaCluster({ cola, frosted, fill }: { cola: Cola; frosted: boolean; fill: string }) {
  const { x, y, len, wid } = cola;
  const rows = Math.max(3, Math.round(len / 3));
  const bumps: { cx: number; cy: number; r: number }[] = [];
  for (let i = 0; i < rows; i++) {
    const t = i / (rows - 1); // 0 at base, 1 at tip
    const rowY = y - len + t * len; // base is lower (larger y)
    const rowW = wid * (1 - 0.7 * t); // taper to the tip
    const r = Math.max(1.6, rowW / 2);
    bumps.push({ cx: x - rowW / 4, cy: rowY, r });
    bumps.push({ cx: x + rowW / 4, cy: rowY, r });
    if (i % 2 === 0) bumps.push({ cx: x, cy: rowY - r * 0.4, r: r * 0.9 });
  }
  return (
    <g>
      <g fill={fill}>
        {bumps.map((b, i) => (
          <circle key={i} cx={b.cx} cy={b.cy} r={b.r} />
        ))}
      </g>
      {frosted && (
        <>
          {/* amber pistil hairs */}
          <g stroke="#d98a3d" strokeWidth="0.7" strokeLinecap="round" opacity="0.85">
            {bumps
              .filter((_, i) => i % 3 === 0)
              .map((b, i) => (
                <line key={i} x1={b.cx} y1={b.cy} x2={b.cx + (i % 2 ? 2.5 : -2.5)} y2={b.cy - 2.2} />
              ))}
          </g>
          {/* trichome frost */}
          <g fill="#eaf6e0" opacity="0.75">
            {bumps.map((b, i) => (
              <circle key={i} cx={b.cx + (i % 2 ? 0.8 : -0.8)} cy={b.cy - 0.8} r="0.8" />
            ))}
          </g>
        </>
      )}
    </g>
  );
}

export function PlantVisual({
  stage,
  flags,
  size = 140,
}: {
  stage: GrowthStage;
  flags: ConditionFlag[];
  size?: number;
}) {
  const dom = dominantFlag(flags);
  const visual = CONDITION_VISUALS[dom.condition];
  const stress = SEVERITY_SCALE[dom.severity];
  const leafFill = visual.tint ?? "#4f9e1f";
  const dead = dom.condition === "dead";
  const plant = buildPlant(stage);

  const bodyStyle: CSSProperties = { ["--stress" as string]: stress };
  const overlays = Array.from(
    new Set(flags.map((f) => CONDITION_VISUALS[f.condition].overlay)),
  ).filter((o) => o !== "none") as Overlay[];

  // Bud greens shift toward pale/amber at harvest; suppressed when dead.
  const budFill = stage === "harvest" ? "#b6c46a" : "#86c33f";

  return (
    <svg
      viewBox="0 0 100 120"
      width={size}
      height={size * 1.2}
      className="select-none"
      role="img"
      aria-label={visual.label}
    >
      <defs>
        <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#9fd4ff" stopOpacity="0" />
          <stop offset="50%" stopColor="#cdeaff" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#9fd4ff" stopOpacity="0" />
        </linearGradient>
        {/* one reusable 7-leaflet cannabis fan leaf (unit size, tip up) */}
        <g id="cleaf">
          {LEAFLETS.map((b, i) => (
            <path key={i} d={BLADE} transform={`rotate(${b.a}) scale(${0.5 * b.s} ${b.s})`} />
          ))}
        </g>
      </defs>

      {/* pot + soil */}
      <path d="M32 104 L68 104 L63 118 L37 118 Z" fill="#7a4a2b" />
      <rect x="30" y="100" width="40" height="6" rx="2" fill="#8a5733" />
      <ellipse cx="50" cy="102" rx="18" ry="3.5" fill="#3a2a1c" />

      <g className={`gpe-body gpe-anim-${visual.bodyAnim}`} style={bodyStyle}>
        {plant.sprout ? (
          /* seed / germination: a small sprout, not a full plant */
          <>
            <ellipse cx="50" cy="101" rx="9" ry="3" fill="#2e2014" />
            {stage !== "seed" && (
              <rect x="49.2" y={plant.stemTop} width="1.6" height={101 - plant.stemTop} fill="#4f9e1f" />
            )}
            {stage === "seed" ? (
              <path d="M50 101 q-3 -6 0 -9 q3 3 0 9" fill="#6fbf3a" />
            ) : (
              <g fill="#6fbf3a">
                <ellipse cx="46" cy={plant.stemTop} rx="4" ry="2.4" transform={`rotate(-25 46 ${plant.stemTop})`} />
                <ellipse cx="54" cy={plant.stemTop} rx="4" ry="2.4" transform={`rotate(25 54 ${plant.stemTop})`} />
              </g>
            )}
            {/* germination's first true serrated leaves */}
            {plant.leaves.map((lf, i) => (
              <use
                key={i}
                href="#cleaf"
                fill={leafFill}
                transform={`translate(${lf.x} ${lf.y}) rotate(${lf.angle}) scale(${lf.size})`}
              />
            ))}
          </>
        ) : (
          <>
            {/* main stalk */}
            <rect x="48.6" y={plant.stemTop} width="2.8" height={104 - plant.stemTop} rx="1.4" fill="#3f7d1a" />
            {/* branches (flowering/harvest) */}
            <g stroke="#3f7d1a" strokeWidth="2" strokeLinecap="round">
              {plant.branches.map((br, i) => (
                <line key={i} x1={br.x1} y1={br.y1} x2={br.x2} y2={br.y2} />
              ))}
            </g>
            {/* fan leaves at every node */}
            {plant.leaves.map((lf, i) => (
              <use
                key={i}
                href="#cleaf"
                fill={leafFill}
                transform={`translate(${lf.x} ${lf.y}) rotate(${lf.angle}) scale(${lf.size})`}
              />
            ))}
            {/* colas at crown + branch tips */}
            {!dead &&
              plant.colas.map((c, i) => (
                <ColaCluster key={i} cola={c} frosted={plant.frosted} fill={budFill} />
              ))}
          </>
        )}
      </g>

      {overlays.map((o) => (
        <Overlays key={o} overlay={o} />
      ))}
    </svg>
  );
}
