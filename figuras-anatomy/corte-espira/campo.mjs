// Líneas de campo en el plano del corte (y = 0), que corta la espira por su centro y atraviesa sus dos lados.
// Dos corrientes opuestas (los dos lados de la espira, 3 vueltas cada uno) y, a 55 kHz, un chasis de acero que
// se comporta casi como un conductor perfecto (profundidad de penetración 0.087 mm): el campo no entra en la
// lámina, lo que se modela con corrientes imagen opuestas reflejadas en el plano z = h. El potencial vector
// A(x, z) es constante a lo largo de cada línea de campo, así que las líneas son curvas de nivel de A.

export function potencial(x, z, { xs = 90, zw = -3, h }) {
  const zi = 2 * h - zw;
  const l = (cx, cz) => 0.5 * Math.log((x - cx) ** 2 + (z - cz) ** 2);
  return l(-xs, zw) - l(-xs, zi) - l(xs, zw) + l(xs, zi);
}

// Curvas de nivel por cuadrados marchantes sobre una malla; devuelve polilíneas [[x, z], ...] con `closed`.
export function curvas(fn, levels, { x0, x1, z0, z1, step = 0.5 }) {
  const nx = Math.round((x1 - x0) / step);
  const nz = Math.round((z1 - z0) / step);
  const V = [];
  for (let j = 0; j <= nz; j++) {
    const row = new Float64Array(nx + 1);
    for (let i = 0; i <= nx; i++) row[i] = fn(x0 + i * step, z0 + j * step);
    V.push(row);
  }
  const out = [];
  for (const level of levels) {
    const pt = new Map();
    const key = (kind, i, j) => `${kind}${i},${j}`;
    const edgePoint = (kind, i, j) => {
      const k = key(kind, i, j);
      if (pt.has(k)) return k;
      let a, b, pa, pb;
      if (kind === "h") { a = V[j][i]; b = V[j][i + 1]; pa = [x0 + i * step, z0 + j * step]; pb = [x0 + (i + 1) * step, z0 + j * step]; }
      else { a = V[j][i]; b = V[j + 1][i]; pa = [x0 + i * step, z0 + j * step]; pb = [x0 + i * step, z0 + (j + 1) * step]; }
      const t = (level - a) / (b - a);
      pt.set(k, [pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t]);
      return k;
    };
    const links = new Map();
    const link = (a, b) => {
      if (!links.has(a)) links.set(a, []);
      if (!links.has(b)) links.set(b, []);
      links.get(a).push(b);
      links.get(b).push(a);
    };
    for (let j = 0; j < nz; j++) {
      for (let i = 0; i < nx; i++) {
        const c = [V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]];
        if (c.some((v) => !Number.isFinite(v))) continue;
        const code = (c[0] > level ? 1 : 0) | (c[1] > level ? 2 : 0) | (c[2] > level ? 4 : 0) | (c[3] > level ? 8 : 0);
        if (code === 0 || code === 15) continue;
        const B = () => edgePoint("h", i, j);
        const Rr = () => edgePoint("v", i + 1, j);
        const T = () => edgePoint("h", i, j + 1);
        const Lf = () => edgePoint("v", i, j);
        const centre = (c[0] + c[1] + c[2] + c[3]) / 4 > level;
        switch (code) {
          case 1: case 14: link(Lf(), B()); break;
          case 2: case 13: link(B(), Rr()); break;
          case 3: case 12: link(Lf(), Rr()); break;
          case 4: case 11: link(Rr(), T()); break;
          case 6: case 9: link(B(), T()); break;
          case 7: case 8: link(Lf(), T()); break;
          case 5: if (centre) { link(Lf(), T()); link(B(), Rr()); } else { link(Lf(), B()); link(Rr(), T()); } break;
          case 10: if (centre) { link(Lf(), B()); link(Rr(), T()); } else { link(Lf(), T()); link(B(), Rr()); } break;
        }
      }
    }
    const seen = new Set();
    const walk = (start) => {
      const line = [start];
      seen.add(start);
      let prev = null, here = start;
      for (;;) {
        const next = (links.get(here) || []).find((n) => n !== prev && !seen.has(n));
        if (!next) break;
        line.push(next);
        seen.add(next);
        prev = here;
        here = next;
      }
      return line;
    };
    // Open curves first (start from an end), then the closed loops.
    for (const [k, ns] of links) if (ns.length === 1 && !seen.has(k)) out.push({ level, closed: false, points: walk(k).map((q) => pt.get(q)) });
    for (const [k] of links) if (!seen.has(k)) {
      const line = walk(k);
      out.push({ level, closed: true, points: line.map((q) => pt.get(q)) });
    }
  }
  return out;
}

// Reduce una polilínea a puntos separados al menos `gap`.
export function thin(points, gap = 1.2, closed = false) {
  const out = [points[0]];
  for (const p of points.slice(1)) {
    const q = out[out.length - 1];
    if (Math.hypot(p[0] - q[0], p[1] - q[1]) >= gap) out.push(p);
  }
  if (!closed) out.push(points[points.length - 1]);
  return out;
}

// Chasis de tamaño finito: la sección del piso (polígono en x, z) como conductor perfecto aislado. Se reparten
// corrientes lineales desconocidas sobre su contorno y se pide que A sea la misma en todo el contorno, con
// corriente neta cero (corrientes de Foucault cerradas). Es el método de elementos de contorno más sencillo.
export function conPiso(outline, { xs = 90, zw = -3, spacing = 1 } = {}) {
  const src = [];
  for (let i = 0; i < outline.length; i++) {
    const a = outline[i], b = outline[(i + 1) % outline.length];
    const n = Math.max(1, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / spacing));
    for (let j = 0; j < n; j++) src.push([a[0] + ((b[0] - a[0]) * j) / n, a[1] + ((b[1] - a[1]) * j) / n]);
  }
  const N = src.length;
  const col = src.map((p, i) => { const q = src[(i + 1) % N]; return [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]; });
  const wires = (x, z) => 0.5 * (Math.log((x + xs) ** 2 + (z - zw) ** 2) - Math.log((x - xs) ** 2 + (z - zw) ** 2));
  // unknowns c_0..c_{N-1}, C:  sum_j c_j ln r_ij - C = -wires(i);  sum_j c_j = 0
  const M = N + 1;
  const a = Array.from({ length: M }, () => new Float64Array(M + 1));
  for (let i = 0; i < N; i++) {
    const [x, z] = col[i];
    for (let j = 0; j < N; j++) a[i][j] = 0.5 * Math.log((x - src[j][0]) ** 2 + (z - src[j][1]) ** 2);
    a[i][N] = -1;
    a[i][M] = -wires(x, z);
  }
  for (let j = 0; j < N; j++) a[N][j] = 1;
  for (let c = 0; c < M; c++) {
    let p = c;
    for (let r = c + 1; r < M; r++) if (Math.abs(a[r][c]) > Math.abs(a[p][c])) p = r;
    [a[c], a[p]] = [a[p], a[c]];
    for (let r = 0; r < M; r++) {
      if (r === c) continue;
      const f = a[r][c] / a[c][c];
      if (f) for (let k = c; k <= M; k++) a[r][k] -= f * a[c][k];
    }
  }
  const cs = Array.from({ length: N }, (_, i) => a[i][M] / a[i][i]);
  const C = a[N][M] / a[N][N];
  const fn = (x, z) => {
    let v = wires(x, z);
    for (let j = 0; j < N; j++) v += cs[j] * 0.5 * Math.log((x - src[j][0]) ** 2 + (z - src[j][1]) ** 2);
    return v;
  };
  return { fn, C };
}

export function inside(poly, [x, z]) {
  let hit = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, zi] = poly[i], [xj, zj] = poly[j];
    if ((zi > z) !== (zj > z) && x < ((xj - xi) * (z - zi)) / (zj - zi) + xi) hit = !hit;
  }
  return hit;
}
