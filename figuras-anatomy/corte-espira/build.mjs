// Fig 1 · Detector de espira bajo un Spark y un Kwid.
// node build.mjs            -> corte-espira.html (oscuro)
// node build.mjs --light    -> corte-espira-light.html (claro)
// node build.mjs --audit    -> además corre la auditoría de geometría del kit
//
// Unidades del mundo: 1 = 1 cm. La espira (180 cm), las alturas libres (15 y 18 cm), la profundidad de la ranura
// (5 cm) y las capas del pavimento van a escala. El ancho de la ranura, los alambres y el espesor de la lámina se
// dibujan ampliados (lo dice el pie de figura).
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../kit/iso-kit.mjs";
import * as G from "../kit/lathe.mjs";
import { tubePieces, tubeSvg } from "../kit/tube.mjs";
import * as A from "../kit/audit.mjs";
import { kitScript } from "../kit/inline-kit.mjs";
import { CARROS, ESPIRA, DELTA_ACERO_MM, lectura } from "./modelo.mjs";
import { curvas, thin, conPiso, inside } from "./campo.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const THEME = process.argv.includes("--light") ? "light" : "dark";

const W = 600;
const H = 420;
const H0 = process.env.H0 ? +process.env.H0 : CARROS[0].altura; // the pan is built at the Spark's clearance and moved by the live code

// ---------- world plan ----------
const BLOCK = { x: -112, y: -130, w: 224, d: 130, r: 0 }; // asphalt + base, cut face at y = 0
const ASPH = 10; // asphalt layer, cm
const BASE = 14; // granular base, cm
const ZB = -(ASPH + BASE);
const WALK = { x: -150, y: -130, w: 26, d: 130, r: 0 }; // sidewalk slab
const CURB = { x: -124, y: -130, w: 12, d: 130, r: 0 };
const WALK_TOP = 15;
const CURB_TOP = 16;
const XS = ESPIRA.lado / 2; // loop legs at x = ±90
const BACK = -90; // back leg of the loop
const CH = 12; // 45° saw cuts at the corners
const SW = 4; // slot width as drawn (true 0.6 cm)
const SD = ESPIRA.ranura.profundidad; // 5 cm, true
const WR = 0.68; // wire radius as drawn
const WIRE_Z = [-SD + WR + 0.1, -SD + 3 * WR + 0.2, -SD + 5 * WR + 0.3];
const SEAL = -SD + 6 * WR + 0.45;
const LEAD_Y = -84;

const PAN_Y0 = -52;
const PAN_Y1 = 0;

const AZ = +(process.env.AZ || 64);
const EL = +(process.env.EL || 30);
const P = k.fitProjection(
  [...k.boxCorners({ ...BLOCK, x: WALK.x, w: BLOCK.x + BLOCK.w - WALK.x }, ZB, 0), [-152, -108, 82], [-152, -120, 82], [72, -118, 58], [80, 0, H0 + 30]],
  W,
  H,
  { pad: 26, azimuth: AZ, elevation: EL },
);
const V = G.viewOf(P);
const KS = G.scaleOf(P);
const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const Ln = (d, style) => k.lineSvg(d, style);
const Dots = (points, style) => k.dotsSvg(points, style);
const path3 = (points, closed = false) => k.pathOf(points.map(at), closed);

const R = A.recorder(P);
const record = R.solid;
function put(name, ref, svg, shapes = [], { bias = 0, ...rest } = {}) {
  return R.put({ name, at: ref, bias, svg, shapes, piece: "fig", ...rest });
}
const PAN_ATTR = ` data-move="pan"`;

function slab(name, plan, z, h, style = {}, { steps = 2, bevel = 0, extra = "", inner = "", bias = 0, meta = {}, attrs } = {}) {
  const shape = record(A.slab(plan, z, h, { name, ...meta }, steps));
  put(name, [plan.x + plan.w / 2, plan.y + plan.d / 2, z + h / 2], S(k.slabOf(plan, z, h, P, steps, bevel), { tone: "mid", ...style, inner }) + extra, [shape], { bias, attrs });
  return shape;
}
function cyl(name, cx, cy, r, z, h, style = {}, { steps = 28, bevel = 0, extra = "", inner = "", bias = 0, meta = {}, attrs } = {}) {
  const shape = record(A.cylinder(cx, cy, r, z, h, { name, ...meta }));
  put(name, [cx, cy, z + h / 2], S(k.cylinder(cx, cy, r, z, h, P, steps, bevel), { tone: "mid", ...style, inner }) + extra, [shape], { bias, attrs });
  return shape;
}
// A prism along y (a section of the floor pan): polygon in (x, z), from y0 to y1.
const FY = G.frameOf([0, 0, 0], [0, 1, 0], [1, 0, 0], [0, 0, 1]);
function prismY(name, poly, y0, y1, style = {}, { extra = "", bias = 0, meta = {}, attrs } = {}) {
  const shape = record(A.prism(FY, poly, y0, y1, { name, ...meta }));
  const cx = poly.reduce((a, p) => a + p[0], 0) / poly.length;
  const cz = poly.reduce((a, p) => a + p[1], 0) / poly.length;
  put(name, [cx, (y0 + y1) / 2, cz], S(G.prismOf(FY, poly, y0, y1, P), { tone: "hi", ...style }) + extra, [shape], { bias, attrs });
  return shape;
}
function turned(name, F, profile, style = {}, { extra = "", bias = 0, meta = {}, attrs, steps } = {}) {
  const paths = G.solidOf(profile, F, P, steps ? { steps } : {});
  const shape = record(A.solid(F, profile, { name, ...meta }));
  const mid = (profile[0][0] + profile[profile.length - 1][0]) / 2;
  put(name, G.add3(F.o, G.mul3(F.a, mid)), S(paths, { tone: "mid", ...style }) + extra, [shape], { bias, attrs });
  return shape;
}

// ---------- static ground: sidewalk, curb, pavement block ----------
const back = [];
back.push(`<path class="iso-halo" d="${k.haloOf({ x: WALK.x, y: BLOCK.y, w: BLOCK.x + BLOCK.w - WALK.x, d: BLOCK.d, r: 2 }, ZB, 1, P)}"/>`);

// faces of the cut (y = 0): a point on the cut face
const cut = (x, z) => at([x, 0, z]);
const cutPath = (pts, closed = false) => k.pathOf(pts.map(([x, z]) => cut(x, z)), closed);
const cutRing = (x, z, r, steps = 18) => k.sideRing([x, 0, z], r, "y", P, steps);

// aggregate: small closed stones on the cut face, seeded so the build is repeatable
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
function stones(x0, x1, z0, z1, count, size, avoid = () => false) {
  const out = [];
  for (let n = 0, tries = 0; n < count && tries < count * 20; tries++) {
    const x = x0 + rnd() * (x1 - x0);
    const z = z0 + rnd() * (z1 - z0);
    const r = size * (0.55 + rnd() * 0.6);
    if (avoid(x, z, r)) continue;
    const sides = 5 + Math.floor(rnd() * 3);
    const phase = rnd() * 6.28;
    const pts = Array.from({ length: sides }, (_, i) => {
      const a = phase + (i / sides) * Math.PI * 2;
      const rr = r * (0.75 + rnd() * 0.4);
      return [x + Math.cos(a) * rr * 1.3, z + Math.sin(a) * rr * 0.8];
    });
    out.push(cutPath(pts, true));
    n++;
  }
  return out.join("");
}
const nearSlot = (x, z, r) => Math.abs(Math.abs(x) - XS) < SW / 2 + r + 1.2 && z > -SD - r - 1.2;

// base course (stand.*: the ground everything stands on)
record(A.slab(BLOCK, ZB, BASE, { name: "stand.base", ground: true }, 2));
back.push(
  S(k.slabOf(BLOCK, ZB, BASE, P, 2), { tone: "lo" }),
  Ln(stones(BLOCK.x + 3, BLOCK.x + BLOCK.w - 3, ZB + 2.2, -ASPH - 2.2, 46, 1.6), { tone: "faint" }),
);
// asphalt layer
record(A.slab(BLOCK, -ASPH, ASPH, { name: "stand.asphalt", ground: true }, 2));
const asphStones = stones(BLOCK.x + 2, BLOCK.x + BLOCK.w - 2, -ASPH + 1.4, -1.2, 70, 0.7, nearSlot);
back.push(S(k.slabOf(BLOCK, -ASPH, ASPH, P, 2), { tone: "mid", crease: "lo" }), Ln(asphStones, { tone: "faint" }));

// the front-right corner of the block (two visible faces meet): a crease the field lines can end on
back.push(Ln(k.pathOf([at([BLOCK.x + BLOCK.w, 0, ZB]), at([BLOCK.x + BLOCK.w, 0, 0])]), { tone: "faint" }));
// sidewalk and curb
record(A.slab(WALK, ZB, WALK_TOP - ZB, { name: "stand.walk", ground: true }, 2));
record(A.slab(CURB, ZB, CURB_TOP - ZB, { name: "stand.curb", ground: true }, 2));
const walkJoints = [-95, -55].map((y) => k.lineOnTop([WALK.x, y], [WALK.x + WALK.w, y], WALK_TOP, P)).join("");
back.push(
  S(k.slabOf(WALK, ZB, WALK_TOP - ZB, P, 2), { tone: "lo", inner: Ln(walkJoints, { tone: "faint" }) }),
  Ln(stones(WALK.x + 2, WALK.x + WALK.w - 2, ZB + 2, WALK_TOP - 2, 30, 1.2), { tone: "faint" }),
);
const curbJoints = [-90, -45].map((y) => k.pathOf([at([CURB.x + CURB.w, y, CURB_TOP]), at([CURB.x + CURB.w, y, 0])])).join("") +
  [-90, -45].map((y) => k.lineOnTop([CURB.x, y], [CURB.x + CURB.w, y], CURB_TOP, P)).join("");
back.push(S(k.slabOf(CURB, ZB, CURB_TOP - ZB, P, 2, 0.6), { tone: "mid", inner: Ln(curbJoints, { tone: "faint" }) }));
// curb face below the pavement line is buried: draw the pavement-curb joint
back.push(Ln(k.pathOf([at([CURB.x + CURB.w, BLOCK.y, 0]), at([CURB.x + CURB.w, 0, 0])]), { tone: "lo" }));

// ---------- the slot on the pavement top: sealant strips ----------
const strip = (a, b, w) => {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const L = Math.hypot(dx, dy);
  const nx = (-dy / L) * w / 2, ny = (dx / L) * w / 2;
  return [[a[0] + nx, a[1] + ny], [b[0] + nx, b[1] + ny], [b[0] - nx, b[1] - ny], [a[0] - nx, a[1] - ny]];
};
const LOOP = [[-XS, 0], [-XS, BACK + CH], [-XS + CH, BACK], [XS - CH, BACK], [XS, BACK + CH], [XS, 0]];
// one outline for the loop's slot (an offset polyline both sides), closed at the cut face
function offsetLine(pts, d) {
  const out = [];
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i];
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let n0 = null, n1 = null;
    if (i > 0) { const dx = p[0] - a[0], dy = p[1] - a[1], L = Math.hypot(dx, dy); n0 = [-dy / L, dx / L]; }
    if (i < pts.length - 1) { const dx = b[0] - p[0], dy = b[1] - p[1], L = Math.hypot(dx, dy); n1 = [-dy / L, dx / L]; }
    if (!n0) n0 = n1;
    if (!n1) n1 = n0;
    const m = [n0[0] + n1[0], n0[1] + n1[1]];
    const ml = Math.hypot(...m);
    const s = d / ((m[0] / ml) * n0[0] + (m[1] / ml) * n0[1]);
    out.push([p[0] + (m[0] / ml) * s, p[1] + (m[1] / ml) * s]);
  }
  return out;
}
const slotRing = [...offsetLine(LOOP, SW / 2), ...offsetLine(LOOP, -SW / 2).reverse()];
const leadRing = strip([-XS + CH / 2 - 0.8, LEAD_Y], [BLOCK.x, LEAD_Y], SW * 0.8);
const sealTop = (ring) => `<path class="cs-seal" d="${k.onTop(ring, 0, P, true)}"/>` + Ln(k.onTop(ring, 0, P, true), { tone: "mid" });
// painted stall line (white paint) and stop bar: flat inlays
const paint = [strip([104, -6], [104, -124], 2.4)];
back.push(...paint.map((ring) => `<path class="cs-paint" d="${k.onTop(ring, 0, P, true)}"/>` + Ln(k.onTop(ring, 0, P, true), { tone: "faint" })));
// asphalt surface: sparse exposed aggregate, kept off the slots and the paint
const grit = [];
for (let n = 0; n < 900 && grit.length < 150; n++) {
  const x = BLOCK.x + 3 + rnd() * (BLOCK.w - 6), y = BLOCK.y + 3 + rnd() * (BLOCK.d - 6);
  const nearLoop = Math.abs(Math.abs(x) - XS) < 4 || Math.abs(y - BACK) < 4 || Math.abs(y - LEAD_Y) < 4 || Math.abs(x - 104) < 3;
  if (!nearLoop) grit.push(at([x, y, 0]));
}
back.push(Dots(grit, { size: 0.35, tone: "lo" }));
back.push(sealTop(leadRing), sealTop(slotRing));
// lead-in enters the curb through a sleeve
back.push(Ln(k.sideRing([CURB.x + CURB.w, LEAD_Y, -1.4], 1.3, "x", P, 16), { tone: "mid" }));
// patched trench in the sidewalk from the curb to the pull box
const TRENCH = strip([CURB.x, LEAD_Y], [-140, LEAD_Y], 3);
back.push(`<path class="cs-seal" d="${k.onTop(TRENCH.map(([x, y]) => [x, y]), WALK_TOP, P, true)}"/>` + Ln(k.onTop(TRENCH, WALK_TOP, P, true), { tone: "lo" }));

// ---------- the cut face: slot sections, wires, field ----------
function slotSection(xc, sign) {
  const out = [];
  const x0 = xc - SW / 2, x1 = xc + SW / 2;
  out.push(`<path class="cs-slot" d="${cutPath([[x0, 0], [x0, -SD], [x1, -SD], [x1, 0]], true)}"/>`);
  out.push(`<path class="cs-seal" d="${cutPath([[x0, 0], [x0, SEAL], [x1, SEAL], [x1, 0]], true)}"/>`);
  out.push(Ln(cutPath([[x0, SEAL], [x1, SEAL]]), { tone: "lo" }));
  out.push(Ln(cutPath([[x0, 0], [x0, -SD], [x1, -SD], [x1, 0]]), { tone: "hi" }));
  for (const z of WIRE_Z) {
    out.push(`<path class="cs-wire" d="${cutRing(xc, z, WR)}"/>`, Ln(cutRing(xc, z, WR), { tone: "hi" }));
    out.push(`<path class="cs-copper" d="${cutRing(xc, z, WR * 0.58)}"/>`);
    out.push(mark(xc, z, WR * 0.58, sign));
  }
  return out.join("");
}
// current through the cut plane: dot = toward the viewer, cross = away
function mark(x, z, r, sign, tone = "hi") {
  if (sign > 0) return Dots([cut(x, z)], { size: r * KS * 0.42, tone });
  const d = r * 0.7071;
  return Ln(cutPath([[x - d, z - d], [x + d, z + d]]) + cutPath([[x - d, z + d], [x + d, z - d]]), { tone }) + Ln(cutRing(x, z, r, 14), { tone: "faint" });
}
back.push(slotSection(-XS, 1), slotSection(XS, -1));

// ---------- field lines (two sets, one per car; crossfaded live) ----------
// the steel section as one outline (x, z) at clearance hh: sills, floor, tunnel walls and top
const panOutline = (hh) => [
  [-80, hh + 1], [-79, hh], [-67, hh], [-66, hh + 1], [-66, hh + 2.4], [-17, hh + 2.4], [-15.8, hh + 2.4], [-10.8, hh + 13],
  [10.8, hh + 13], [15.8, hh + 2.4], [17, hh + 2.4], [66, hh + 2.4], [66, hh + 1], [67, hh], [79, hh], [80, hh + 1],
  [80, hh + 8], [66, hh + 8], [66, hh + 3.6], [17, hh + 3.6], [12, hh + 14.2], [-12, hh + 14.2], [-17, hh + 3.6], [-66, hh + 3.6], [-66, hh + 8], [-80, hh + 8],
];
// one line through each seed: small loops round each side of the loop, and wide lines that must squeeze
// between the pavement and the steel and wrap round its edge
const SEEDS = [4.5, 8.5, 13.5, 30, 44, 60];
const FIELD_TOP = 12; // above the clearance: lines fade out just after they turn round the sill
function fieldSet(hh) {
  const body = panOutline(hh);
  const zw = (WIRE_Z[0] + WIRE_Z[2]) / 2;
  const { fn, C } = conPiso(body, { xs: XS, zw, spacing: 0.8 });
  const f = (x, z) => fn(x, z) - C;
  const levels = SEEDS.flatMap((d) => { const v = f(-XS + d, zw); return [v, -v]; });
  const grow = body.map(([x, z]) => [x * 1.006, hh + 7 + (z - hh - 7) * 1.04]);
  const lines = curvas(f, levels, { x0: CURB.x, x1: BLOCK.x + BLOCK.w, z0: ZB, z1: hh + FIELD_TOP, step: 0.5 });
  const onEdge = (p) => Math.abs(p[1] - ZB) < 0.6 || (Math.abs(p[0] - BLOCK.x - BLOCK.w) < 0.6 && p[1] <= 0.3) || (Math.abs(p[0] - CURB.x) < 0.6 && p[1] <= CURB_TOP);
  const out = [];
  for (const c of lines) {
    const runs = [];
    let run = [];
    for (const p of c.points) {
      if (inside(grow, p)) { if (run.length) runs.push(run); run = []; } else run.push(p);
    }
    if (run.length) runs.push(run);
    if (c.closed && runs.length === 2 && !inside(grow, c.points[0])) { runs[0] = [...runs[1], ...runs[0]]; runs.pop(); }
    const closed = c.closed && runs.length === 1;
    for (const r of runs) {
      if (r.length < 10) continue;
      const pts = thin(r, 1.1, closed);
      if (closed) { out.push(Ln(cutPath(pts, true), { tone: "mid" })); continue; }
      const fade = [onEdge(pts[0]) ? 0 : 16, onEdge(pts[pts.length - 1]) ? 0 : 16];
      out.push(fade[0] || fade[1] ? k.fadeLineSvg(pts.map(([x, z]) => cut(x, z)), { fade, tone: "mid" }) : Ln(cutPath(pts), { tone: "mid" }));
    }
  }
  return out.join("");
}
const FIELD = CARROS.map((c) => fieldSet(c.altura));

// ---------- floor pan (moves) ----------
const PAN = [];
const panMeta = { owner: "pan", ground: true }; // held by its own wheels, outside the section
const h = H0;
const T = 1.2; // sheet thickness as drawn
const SILL = [[-80, h + 1], [-79, h], [-67, h], [-66, h + 1], [-66, h + 8], [-80, h + 8]];
const mirror = (poly) => poly.map(([x, z]) => [-x, z]).reverse();
const FLOOR = [[-66, h + 2.4], [-17, h + 2.4], [-17, h + 2.4 + T], [-66, h + 2.4 + T]];
const WALL = [[-17, h + 2.4], [-15.8, h + 2.4], [-10.8, h + 13], [-12, h + 13]];
const TUN = [[-12, h + 13], [12, h + 13], [12, h + 13 + T], [-12, h + 13 + T]];
const panBits = [];
// skin layer: lit hairline along the bottom of every cut section
const skin = (poly) => {
  const zMin = Math.min(...poly.map(([, z]) => z));
  const xs = poly.filter(([, z]) => Math.abs(z - zMin) < 0.01).map(([x]) => x);
  return Ln(cutPath([[Math.min(...xs), zMin + 0.12], [Math.max(...xs), zMin + 0.12]]), { tone: "lit" });
};
// eddy current paths on the visible face of the steel, along the loop's sides
const eddyOn = (xList, z) => Ln(xList.map((x) => k.pathOf([at([x, PAN_Y0, z]), at([x, PAN_Y1, z])])).join(""), { tone: "lit" });
prismY("pan.sill.l", SILL, PAN_Y0, PAN_Y1, {}, {
  meta: panMeta, attrs: PAN_ATTR,
  extra: skin(SILL) + eddyOn([-76, -72], h + 8) + Dots([-62, -50, -38, -26, -14, -4].map((y) => at([-73, y, h + 8])), { size: 0.45 }) + mark(-73, h + 1.6, 0.9, -1, "lit"),
});
prismY("pan.sill.r", mirror(SILL), PAN_Y0, PAN_Y1, {}, {
  meta: panMeta, attrs: PAN_ATTR,
  extra: skin(mirror(SILL)) + eddyOn([72, 76], h + 8) + Dots([-62, -50, -38, -26, -14, -4].map((y) => at([73, y, h + 8])), { size: 0.45 }) + mark(73, h + 1.6, 0.9, 1, "lit"),
});
const grommets = (side) => { const pts = [[side * 32, -12], [side * 32, -45]]; return Ln(pts.map(([x, y]) => k.ring(x, y, 1.8, h + 2.4 + T, P, 16) + k.ring(x, y, 0.9, h + 2.4 + T, P, 12)).join(""), { tone: "lo" }); };
const beads = (x0, x1) => [x0 + 8, x0 + 16, x1 - 16].map((x) => k.pathOf([at([x, PAN_Y0, h + 2.4 + T]), at([x, PAN_Y1, h + 2.4 + T])])).join("");
prismY("pan.floor.l", FLOOR, PAN_Y0, PAN_Y1, {}, { meta: panMeta, attrs: PAN_ATTR, extra: Ln(beads(-66, -17), { tone: "faint" }) + grommets(-1) + skin(FLOOR) + eddyOn([-62], h + 2.4 + T) });
prismY("pan.floor.r", mirror(FLOOR), PAN_Y0, PAN_Y1, {}, { meta: panMeta, attrs: PAN_ATTR, extra: Ln(beads(17, 66), { tone: "faint" }) + grommets(1) + skin(mirror(FLOOR)) + eddyOn([62], h + 2.4 + T) });
prismY("pan.wall.l", WALL, PAN_Y0, PAN_Y1, {}, { meta: panMeta, attrs: PAN_ATTR });
prismY("pan.wall.r", mirror(WALL), PAN_Y0, PAN_Y1, {}, { meta: panMeta, attrs: PAN_ATTR });
prismY("pan.tunnel", TUN, PAN_Y0, PAN_Y1, {}, { meta: panMeta, attrs: PAN_ATTR });
// seat cross-members on the floor
for (const [side, x0] of [["l", -62], ["r", 21]]) {
  const plan = { x: x0, y: -36, w: 41, d: 9, r: 0.6 };
  slab(`pan.cross.${side}`, plan, h + 2.4 + T, 4, { tone: "hi" }, {
    bevel: 0.5, meta: panMeta, attrs: PAN_ATTR,
    extra: Dots([plan.x + 4, plan.x + plan.w - 4].map((x) => at([x, plan.y + plan.d / 2, h + 2.4 + T + 4])), { size: 0.5 }) +
      Ln([plan.x + 10, plan.x + plan.w - 10].map((x) => k.ring(x, plan.y + plan.d / 2, 1.4, h + 2.4 + T + 4, P, 14)).join(""), { tone: "lo" }),
  });
}
// exhaust pipe in the tunnel, with a hanger
const FX = G.frameAlong([0, PAN_Y0, h + 7.5], [0, 1, 0]);
turned("pan.exhaust", FX, [[0, 2.6], [PAN_Y1 - PAN_Y0, 2.6]], { tone: "mid" }, { meta: { owner: "pan", ground: true }, attrs: PAN_ATTR, extra: Ln(cutRing(0, h + 7.5, 1.9, 24), { tone: "lo" }) });
slab("pan.hanger", { x: -0.7, y: -27, w: 1.4, d: 2.4, r: 0.3 }, h + 10.1, 2.9, { tone: "mid" }, { meta: panMeta, attrs: PAN_ATTR });

// ---------- height gauge standing on the pavement, its jaw under the right sill ----------
const GX = 82;
slab("gauge.foot", { x: GX - 5, y: -9, w: 10, d: 8, r: 1 }, 0, 2, { tone: "mid" }, { bevel: 0.5, extra: Dots([at([GX - 3.2, -2.6, 2]), at([GX + 3.2, -2.6, 2])], { size: 0.45 }) });
const BAR = { x: GX - 1, y: -6, w: 2.2, d: 2, r: 0.2 };
const tickD = [];
const tickM = [];
for (let z = 4; z <= 30; z++) {
  const len = z % 5 === 0 ? 1.4 : 0.7;
  (z % 5 === 0 ? tickM : tickD).push(k.pathOf([at([BAR.x, BAR.y + BAR.d, z]), at([BAR.x + len, BAR.y + BAR.d, z])]));
}
slab("gauge.bar", BAR, 2, 30, { tone: "mid" }, { extra: Ln(tickD.join(""), { tone: "lo" }) + Ln(tickM.join(""), { tone: "mid" }) });
slab("gauge.cap", { x: BAR.x - 0.4, y: BAR.y - 0.4, w: BAR.w + 0.8, d: BAR.d + 0.8, r: 0.4 }, 32, 1.2, { tone: "mid" });
// jaw (slider + arm), moves with the pan: its top touches the sill bottom
// the slider rides on the bar's front face; its arm reaches under the sill
const SLD = { x: BAR.x - 0.8, y: BAR.y + BAR.d, w: BAR.w + 1.6, d: 1.4, r: 0.3 };
slab("gauge.slider", SLD, h - 3.2, 4.4, { tone: "hi" }, { attrs: PAN_ATTR, extra: Dots([at([SLD.x + SLD.w / 2, SLD.y + SLD.d, h - 1.6])], { size: 0.55, tone: "hi" }) + Ln(k.pathOf([at([SLD.x, SLD.y + SLD.d, h - 0.4]), at([SLD.x + SLD.w, SLD.y + SLD.d, h - 0.4])]), { tone: "lit" }) });
slab("gauge.jaw", { x: 76, y: SLD.y + 0.1, w: SLD.x - 76, d: SLD.d - 0.2, r: 0.2 }, h - 1.2, 1.2, { tone: "hi" }, { attrs: PAN_ATTR });

// ---------- tire hint behind the section ----------
const TIRE = { x: 72, y: -118, r: 27, w: 17 };
const FT = G.frameAlong([TIRE.x - TIRE.w / 2, TIRE.y, TIRE.r], [1, 0, 0]);
const tireProfile = [[0, TIRE.r - 5], [0.4, TIRE.r - 2.5], [1.6, TIRE.r - 0.6], [3.4, TIRE.r], [6.6, TIRE.r], [7, TIRE.r - 0.8], [7.4, TIRE.r], [9.6, TIRE.r], [10, TIRE.r - 0.8], [10.4, TIRE.r], [13.6, TIRE.r], [15.4, TIRE.r - 0.6], [16.6, TIRE.r - 2.5], [TIRE.w, TIRE.r - 5]];
turned("tire", FT, tireProfile, { tone: "lo" }, { meta: { ground: true }, steps: 96 });
const FR = G.frameAlong([TIRE.x + TIRE.w / 2, TIRE.y, TIRE.r], [1, 0, 0]);
turned("tire.rim", FR, [[-1.2, TIRE.r - 9], [0, TIRE.r - 9.6]], { tone: "mid" }, { meta: { owner: "tire" }, bias: 0.05, extra: Dots(Array.from({ length: 4 }, (_, i) => { const a = (i / 4) * Math.PI * 2 + 0.4; return at([TIRE.x + TIRE.w / 2, TIRE.y + Math.cos(a) * 5, TIRE.r + Math.sin(a) * 5]); }), { size: 0.6, tone: "mid" }) + Ln(k.sideRing([TIRE.x + TIRE.w / 2, TIRE.y, TIRE.r], 2.6, "x", P, 20), { tone: "lo" }) });

// ---------- pull box, post and detector ----------
const PB = { x: -147, y: -90, w: 14, d: 12, r: 1 };
slab("pull.body", PB, WALK_TOP, 11, { tone: "mid" }, { steps: 3, inner: Ln(k.sideSeam(PB, WALK_TOP + 7.5, P, 3), { tone: "faint" }) });
const PBL = k.insetPlan(PB, -0.5);
slab("pull.lid", PBL, WALK_TOP + 11, 1.2, { tone: "mid" }, { steps: 3, bevel: 0.4, extra: Dots(k.corners(PB, 1.8).map(([x, y]) => at([x, y, WALK_TOP + 12.2])), { size: 0.5 }) + Ln(k.corners(PB, 1.8).map(([x, y]) => k.ring(x, y, 0.9, WALK_TOP + 12.2, P, 12)).join(""), { tone: "lo" }) });
const PBG = [-160, -84 + 0.0];
cyl("pull.gland", PB.x + 9.5, PB.y + 6, 1.7, WALK_TOP + 12.2, 2.2, { tone: "mid" }, { steps: 18 });
const POST = [-138, -114];
cyl("post.base", POST[0], POST[1], 5, WALK_TOP, 1, { tone: "mid" }, { bevel: 0.4, extra: Dots([0, 1, 2, 3].map((i) => { const a = (i / 4) * Math.PI * 2 + 0.78; return at([POST[0] + Math.cos(a) * 3.6, POST[1] + Math.sin(a) * 3.6, WALK_TOP + 1]); }), { size: 0.5 }) });
const POST_TOP = 56;
cyl("post.tube", POST[0], POST[1], 2.4, WALK_TOP + 1, POST_TOP - WALK_TOP - 1, { tone: "mid" }, { inner: Ln(k.sideArc(POST[0], POST[1], 2.4, 30, P, 16), { tone: "faint" }) });
cyl("post.cap", POST[0], POST[1], 4, POST_TOP, 2, { tone: "mid" }, { bevel: 0.3 });
const BOX = { x: -152, y: -120, w: 28, d: 12, r: 1.2 };
const BOX_Z = POST_TOP + 2;
const BOX_H = 22;
const front = BOX.y + BOX.d;
// screen window on the front face (y = front): local u along x from BOX.x, v down from the top
const SCR = { u: 4, v: 4, w: 20, h: 9 };
const faceM = k.sideMatrix([BOX.x, front], BOX_Z + BOX_H, P, "left");
const faceQuad = (u0, v0, u1, v1, dy = 0) => k.pathOf([[u0, v0], [u1, v0], [u1, v1], [u0, v1]].map(([u, v]) => at([BOX.x + u, front + dy, BOX_Z + BOX_H - v])), true);
const screen = [
  `<path class="cs-recess" d="${faceQuad(SCR.u, SCR.v, SCR.u + SCR.w, SCR.v + SCR.h)}"/>`,
  `<path class="cs-screen" d="${faceQuad(SCR.u + 0.6, SCR.v + 0.6, SCR.u + SCR.w - 0.6, SCR.v + SCR.h - 0.6)}"/>`,
  Ln(faceQuad(SCR.u, SCR.v, SCR.u + SCR.w, SCR.v + SCR.h), { tone: "lo" }),
  `<g transform="${faceM}"><clipPath id="cs-scr"><rect x="${SCR.u + 0.6}" y="${SCR.v + 0.6}" width="${SCR.w - 1.2}" height="${SCR.h - 1.2}"/></clipPath>` +
    `<g clip-path="url(#cs-scr)"><text class="cs-digits" data-part="screen-f" x="${SCR.u + SCR.w - 1.6}" y="${SCR.v + 5.6}" font-size="4.4" text-anchor="end">58.8</text>` +
    `<text class="cs-digits cs-small" data-part="screen-u" x="${SCR.u + 1.6}" y="${SCR.v + 7.9}" font-size="1.7">kHz · ΔL −12.9%</text>` +
    `<text class="cs-digits cs-small" data-part="screen-car" x="${SCR.u + 1.6}" y="${SCR.v + 2.5}" font-size="1.6">SPARK</text></g></g>`,
  Dots([at([BOX.x + 6, front, BOX_Z + 7]), at([BOX.x + 9.5, front, BOX_Z + 7])], { size: 0.85, tone: "hi" }),
  Ln([BOX.x + 15, BOX.x + 23].map(() => "").join("") + [0, 1, 2].map((i) => k.pathOf([at([BOX.x + 15, front, BOX_Z + 8 - i * 1.4]), at([BOX.x + (i === 2 ? 20 : 24), front, BOX_Z + 8 - i * 1.4])])).join(""), { tone: "lo", free: true }),
].join("");
const boxSeam = Ln(k.sideSeam(BOX, BOX_Z + BOX_H - 2.2, P, 3), { tone: "faint" });
slab("det.box", BOX, BOX_Z, BOX_H, { tone: "hi", crease: "lo" }, { steps: 3, bevel: 0.6, inner: boxSeam, extra: screen + Dots(k.corners(BOX, 1.8).map(([x, y]) => at([x, y, BOX_Z + BOX_H])), { size: 0.5 }) });
slab("det.hinge", { x: BOX.x - 0.8, y: BOX.y + 2, w: 0.8, d: 8, r: 0.3 }, BOX_Z + BOX_H - 2.2, 1.6, { tone: "mid" });
const GL = [BOX.x + 21, BOX.y + 6];
cyl("det.gland", GL[0], GL[1], 1.7, BOX_Z - 2.4, 2.4, { tone: "mid" }, { steps: 18 });

// twisted-pair lead-in: from the pull box gland up to the detector gland
function cable(name, points, r, { bend = 4, tone = "mid" } = {}) {
  const route = G.fillet(points, Math.max(bend, r * 2.6), 10, { P, tube: r });
  R.route(name, route, r, { limp: true, piece: "fig" });
  tubePieces(route, r, P, { maxLength: 10, spacing: 0.7, rings: { pitch: 1.8, twist: 1.6, cross: false, tone: "lo" } }).forEach((piece, i) =>
    put(`${name}:${i}`, piece.mid, tubeSvg(piece, { tone }), [A.tube(piece.points, piece.radii)], { bias: 0.05, route: name, chunk: i }));
  return route;
}
const C0 = [PB.x + 9.5, PB.y + 6, WALK_TOP + 14.4];
const C1 = [GL[0], GL[1], BOX_Z - 2.4];
cable("leadin", [C0, [C0[0], C0[1], C0[2] + 5], [GL[0], -97, C0[2] + 11], [GL[0], GL[1], C0[2] + 15], C1], 0.85);

// ---------- order, page ----------
A.settle(R, P);
R.items.sort((a, b) => a.key - b.key);
const items = R.items.map((item) => `<g class="it" data-name="${item.name}"${item.attrs ?? ""}>${item.svg}</g>`);

// clip for the field: everything below the pan's front bottom edge (moves with the pan)
const clipY = at([0, 0, H0]);
const ux = G.sub3 ? null : null;
const big = 2000;
const e0 = at([-400, 0, H0]);
const e1 = at([400, 0, H0]);
const clip = `<clipPath id="cs-field-clip"><path data-move="pan" d="M${e0[0].toFixed(1)} ${e0[1].toFixed(1)}L${e1[0].toFixed(1)} ${e1[1].toFixed(1)}L${e1[0].toFixed(1)} ${big}L${e0[0].toFixed(1)} ${big}Z"/></clipPath>`;
const field = `<g class="cs-field">${FIELD.map((d, i) => `<g data-field="${i}" style="opacity:${i === 0 ? 1 : 0}">${d}</g>`).join("")}</g>`;

const svg = k.figureSvg({
  width: W,
  height: H,
  label:
    "Corte de un pavimento de asfalto con la espira de un detector de vehículos: una ranura de 5 cm con tres vueltas de alambre y sellante, cuyo cable de bajada va a una caja de paso y a un detector con pantalla en un poste. Encima, a la altura libre del carro, una sección del piso de acero de un carro con las corrientes de Foucault en su cara inferior; las líneas de campo de la espira se aplastan bajo la lámina.",
  body: [...back, `<path class="iso-halo" style="filter:blur(6px)" d="${k.haloOf({ x: -78, y: PAN_Y0 + 4, w: 156, d: PAN_Y1 - PAN_Y0 - 6, r: 6 }, 0, 0.1, P)}"/>`, ...items, field],
});

const CSS = `
.cs-seal{fill:var(--anatomy-shade-0);stroke:none}
.cs-paint{fill:var(--cs-paint);stroke:none}
.cs-slot{fill:var(--anatomy-paper);stroke:none}
.cs-wire{fill:var(--anatomy-paper);stroke:none}
.cs-copper{fill:var(--cs-copper);stroke:none}
.cs-recess{fill:var(--anatomy-shade-0);stroke:none}
.cs-screen{fill:var(--cs-screen);stroke:none}
.cs-digits{fill:var(--cs-digit);font-family:var(--anatomy-mono);letter-spacing:.02em}
.cs-small{fill:var(--cs-digit-dim)}
.iso{--cs-paint:#2a2a2a;--cs-copper:#5a5a5a;--cs-screen:#0a0a0a;--cs-digit:#e8e8e8;--cs-digit-dim:#8a8a8a}
.iso[data-theme="light"]{--cs-paint:#ffffff;--cs-copper:#9a9a9e;--cs-screen:#1d1d20;--cs-digit:#f4f4f4;--cs-digit-dim:#a8a8ac}
.cs-stage{outline:none}
@media (max-width:560px){.iso-plate-corner[data-corner="title"]{top:18px;left:0;right:auto;font-size:9.5px;letter-spacing:.06em}}
.cs-stage:focus-visible{box-shadow:0 0 0 1px var(--anatomy-mid)}
`;

const DATA = { P, h0: H0, cars: CARROS.map((c) => ({ ...c, text: lectura(c) })) };
const live = `
const D = ${JSON.stringify(DATA)};
const stage = document.querySelector(".cs-stage");
const svg = stage.querySelector("svg");
const movers = [...svg.querySelectorAll('[data-move="pan"]')];
const fields = [...svg.querySelectorAll("[data-field]")];
const readout = document.querySelector("[data-readout]");
const scrF = svg.querySelector('[data-part="screen-f"]');
const scrU = svg.querySelector('[data-part="screen-u"]');
const scrC = svg.querySelector('[data-part="screen-car"]');
const still = matchMedia("(prefers-reduced-motion: reduce)");
let pick = 0, z = D.cars[0].altura, frame = 0, last = 0, clock = 0, touring = !still.matches, visible = false, idle = 0;
function say() {
  const c = D.cars[pick];
  if (readout.textContent !== c.text) readout.textContent = c.text;
  scrF.textContent = c.f_kHz.toFixed(1);
  scrU.textContent = "kHz · ΔL " + c.dLrel.toFixed(1).replace("-", "−") + "%";
  scrC.textContent = c.nombre.toUpperCase();
  stage.setAttribute("aria-valuetext", c.text);
}
function draw() {
  const t = translateAlong(D.P, [0, 0, z - D.h0]);
  for (const el of movers) el.setAttribute("transform", t);
  const a = D.cars[0].altura, b = D.cars[1].altura;
  const w = Math.min(1, Math.max(0, (z - a) / (b - a)));
  const s = w * w * (3 - 2 * w);
  fields[0].style.opacity = (1 - s).toFixed(3);
  fields[1].style.opacity = s.toFixed(3);
}
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  if (touring) {
    clock += dt;
    const next = Math.floor(clock / 3.2) % 2;
    if (next !== pick) { pick = next; say(); }
  }
  const want = D.cars[pick].altura;
  z = still.matches ? want : z + (want - z) * (1 - Math.exp(-dt / 0.35));
  if (Math.abs(want - z) < 0.002) z = want;
  draw();
  frame = visible && (touring || z !== want) ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
const choose = (i) => {
  touring = false;
  if (i !== pick) { pick = i; say(); }
  clearTimeout(idle);
  idle = setTimeout(() => { touring = !still.matches; clock = pick ? 3.2 : 0; run(); }, 4000);
  run();
};
new IntersectionObserver((e) => { visible = e[e.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
stage.addEventListener("pointermove", (e) => { const r = svg.getBoundingClientRect(); choose((e.clientX - r.left) / r.width < 0.5 ? 0 : 1); });
stage.addEventListener("pointerenter", () => {});
stage.addEventListener("keydown", (e) => {
  let to = null;
  if (e.key === "ArrowLeft" || e.key === "1") to = 0;
  if (e.key === "ArrowRight" || e.key === "2") to = 1;
  if (e.key === " " || e.key === "Enter") to = 1 - pick;
  if (to === null) return;
  e.preventDefault();
  choose(to);
});
say();
draw();
`;

const body =
  `<style>${CSS}</style>` +
  k.plateHtml({
    fig: "Fig 1",
    title: "Detector de espira bajo un Spark y un Kwid",
    hint: "Pasa el cursor para cambiar de carro",
    readout: lectura(CARROS[0]),
    keys: [
      { mark: "lit", label: `Corrientes de Foucault en la lámina de acero (profundidad de penetración ${DELTA_ACERO_MM} mm a 55 kHz)` },
      { mark: "raised", label: "Piso del carro a su altura libre: Spark 15 cm, Kwid 18 cm" },
      { mark: "edge", label: "Líneas de campo de la espira en el plano del corte" },
    ],
    caption:
      `Espira cuadrada de ${ESPIRA.lado / 100} m con ${ESPIRA.vueltas} vueltas de alambre 14 AWG en una ranura de ${ESPIRA.ranura.ancho * 10} mm × ${ESPIRA.ranura.profundidad} cm, sellada; el par trenzado sube por la caja de paso al detector LC. Sin carro, L₀ = ${ESPIRA.L0_uH.toFixed(1)} µH y el oscilador marca ${ESPIRA.f0_kHz.toFixed(1)} kHz. El acero no deja entrar el campo: la inductancia baja y la frecuencia sube, más cuanto más bajo va el piso (Spark −12.9 %, 58.8 kHz; Kwid −11.4 %, 58.4 kHz). Pavimento, espira y alturas a escala; el ancho de la ranura, los alambres y el espesor de la lámina están ampliados, y las corrientes, que circulan por la cara inferior, se dibujan sobre la cara visible.`,
    body: `<div class="iso-stage cs-stage" tabindex="0" role="switch" aria-label="Corte de la espira. Flechas izquierda y derecha, o espacio, cambian entre el Spark y el Kwid" aria-valuetext="${lectura(CARROS[0])}">${svg}</div>`,
  });

const name = THEME === "light" ? "corte-espira-light.html" : "corte-espira.html";
const page = k.pageHtml({ title: "Corte de la espira", theme: THEME, body, script: kitScript() + live, width: 680 });
writeFileSync(join(HERE, name), page);
console.log("wrote", name, `${(page.length / 1024).toFixed(0)} KB`, `${R.items.length} items`, `scale ${KS.toFixed(3)}`);

A.auditOrExit(R, P, {});
