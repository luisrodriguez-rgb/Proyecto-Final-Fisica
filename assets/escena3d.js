/* Escena 3D del parqueadero. Los datos (window.__D) salen de sensor/escena.py; aquí solo se dibujan e interpolan. */
(function () {
  const D = window.__D;
  const oscuro = D.tema === "Oscuro";
  if (oscuro) document.documentElement.classList.add("oscuro");
  const C = oscuro
    ? { cieloArriba: 0x0a1330, horizonte: 0xc9825a, suelo: 0x111114, asfalto: 0x2b2d31, acera: 0x55565b,
        linea: 0x8e8e86, campo: 0x4cc8ff, espira: 0xff8a2a, corr: 0xffa13a, poste: 0x5f636b, hemi: 0.35, sol: 0.45,
        humedo: 0.5, farola: 1.4, bloom: [0.6, 0.4, 0.88], env: 0.35, suelo_env: 0.55, exp: 0.9 }
    : { cieloArriba: 0x7fb0e3, horizonte: 0xeceee9, suelo: 0xb7b8b2, asfalto: 0x55585d, acera: 0xc4c3bd,
        linea: 0xf5f5ef, campo: 0x1f6fe0, espira: 0xf26b0f, corr: 0xf59e0b, poste: 0x8c9097, hemi: 0.42, sol: 1.15,
        humedo: 0.88, farola: 0, bloom: [0.25, 0.35, 0.95], env: 0.45, suelo_env: 0.3, exp: 0.82 };

  const canvas = document.getElementById("c");
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true }); }
  catch (e) { document.getElementById("sinwebgl").style.display = "flex"; return; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = C.exp;

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(C.horizonte, 30, 95);
  const camera = new THREE.PerspectiveCamera(36, 1, 0.03, 300);
  const controls = new THREE.OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.495;
  controls.minDistance = 1.0;
  controls.maxDistance = 32;

  // ---------------------------------------------------------------- cielo y reflejos
  function materialCielo() {
    return new THREE.ShaderMaterial({
      side: THREE.BackSide, depthWrite: false, fog: false,
      uniforms: { arriba: { value: new THREE.Color(C.cieloArriba) }, horizonte: { value: new THREE.Color(C.horizonte) },
                  suelo: { value: new THREE.Color(C.suelo) } },
      vertexShader: "varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.0); }",
      fragmentShader: "uniform vec3 arriba, horizonte, suelo; varying vec3 vp;" +
        "void main(){ float h = vp.y; vec3 c = h > 0.0 ? mix(horizonte, arriba, pow(clamp(h*1.6,0.0,1.0),0.7)) : mix(horizonte, suelo, clamp(-h*6.0,0.0,1.0));" +
        " gl_FragColor = vec4(c,1.0); }",
    });
  }
  const cielo = new THREE.Mesh(new THREE.SphereGeometry(150, 32, 16), materialCielo());
  scene.add(cielo);
  const escenaEnv = new THREE.Scene();
  escenaEnv.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), materialCielo()));
  for (const [x, y, z, w, h, k] of [[0, 30, 0, 40, 40, C.env], [30, 8, -20, 25, 8, C.env * 1.6], [-30, 10, 20, 20, 10, C.env * 0.8]]) {
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }));
    panel.material.color.multiplyScalar(k); panel.position.set(x, y, z); panel.lookAt(0, 0, 0); escenaEnv.add(panel);
  }
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(escenaEnv, 0.03).texture;

  scene.add(new THREE.HemisphereLight(C.cieloArriba, C.suelo, C.hemi));
  const sol = new THREE.DirectionalLight(oscuro ? 0xffc9a0 : 0xfff6e8, C.sol);
  sol.position.set(-8, 12, 6);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  sol.shadow.bias = -0.0008;
  sol.shadow.normalBias = 0.035;
  Object.assign(sol.shadow.camera, { left: -13, right: 13, top: 9, bottom: -9, near: 1, far: 45 });
  scene.add(sol);

  // ---------------------------------------------------------------- texturas
  function textura(base, n, rep, ruido) {
    const cv = document.createElement("canvas"); cv.width = cv.height = 512;
    const g = cv.getContext("2d"); const col = new THREE.Color(base);
    g.fillStyle = "#" + col.getHexString(); g.fillRect(0, 0, 512, 512);
    for (let i = 0; i < n; i++) {
      const v = (Math.random() - 0.5) * ruido;
      g.fillStyle = `rgba(${128 + v},${128 + v},${128 + v},0.12)`;
      const s = Math.random() < 0.06 ? 3 : 1.4; g.fillRect(Math.random() * 512, Math.random() * 512, s, s);
    }
    const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rep[0], rep[1]);
    t.encoding = THREE.sRGBEncoding; t.anisotropy = 8; return t;
  }
  function mapaRugosidad() {
    const cv = document.createElement("canvas"); cv.width = cv.height = 256; const g = cv.getContext("2d");
    g.fillStyle = "#bbbbbb"; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 40; i++) {
      const x = Math.random() * 256, y = Math.random() * 256, r = 10 + Math.random() * 40;
      const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, "rgba(40,40,40,0.8)"); gr.addColorStop(1, "rgba(40,40,40,0)");
      g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r);
    }
    const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(6, 2); return t;
  }

  // ---------------------------------------------------------------- pavimento y entorno
  const suelo = new THREE.Mesh(new THREE.PlaneGeometry(90, 9.2),
    new THREE.MeshStandardMaterial({ color: 0xffffff, map: textura(C.asfalto, 9000, [36, 4], 40), roughness: C.humedo,
      roughnessMap: oscuro ? mapaRugosidad() : null, metalness: 0.0, envMapIntensity: C.suelo_env }));
  suelo.rotation.x = -Math.PI / 2; suelo.receiveShadow = true; scene.add(suelo);
  const matAcera = new THREE.MeshStandardMaterial({ color: 0xffffff, map: textura(C.acera, 3000, [30, 2], 30), roughness: 0.85 });
  const matBorde = new THREE.MeshStandardMaterial({ color: oscuro ? 0x7a7b80 : 0xdad9d2, roughness: 0.7 });
  for (const s of [-1, 1]) {
    const acera = new THREE.Mesh(new THREE.BoxGeometry(90, 0.15, 4), matAcera);
    acera.position.set(0, 0.075, s * 6.6); acera.receiveShadow = true; scene.add(acera);
    const borde = new THREE.Mesh(new THREE.BoxGeometry(90, 0.16, 0.22), matBorde);
    borde.position.set(0, 0.08, s * 4.65); borde.receiveShadow = true; borde.castShadow = true; scene.add(borde);
  }
  const zona = new THREE.Mesh(new THREE.PlaneGeometry(200, 200),
    new THREE.MeshStandardMaterial({ color: oscuro ? 0x15171a : 0x9da38f, roughness: 1 }));
  zona.rotation.x = -Math.PI / 2; zona.position.y = -0.01; scene.add(zona);
  const matLinea = new THREE.MeshStandardMaterial({ color: C.linea, roughness: 0.6 });
  for (let x = -40; x < 40; x += 3.2) for (const z of [-2.05, 2.05]) {
    const l = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.004, 0.12), matLinea); l.position.set(x, 0.002, z); scene.add(l);
  }
  const pare = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.004, 3.9), matLinea); pare.position.set(2.7, 0.002, 0); scene.add(pare);
  // flechas pintadas
  const flecha = new THREE.Shape(); flecha.moveTo(0, -0.12); flecha.lineTo(0.7, -0.12); flecha.lineTo(0.7, -0.3);
  flecha.lineTo(1.1, 0); flecha.lineTo(0.7, 0.3); flecha.lineTo(0.7, 0.12); flecha.lineTo(0, 0.12);
  const fl = new THREE.Mesh(new THREE.ShapeGeometry(flecha), matLinea); fl.rotation.x = -Math.PI / 2; fl.position.set(-5.5, 0.003, 0); scene.add(fl);

  function arbol(x, z, s) {
    const g = new THREE.Group();
    const tronco = new THREE.Mesh(new THREE.CylinderGeometry(0.08 * s, 0.11 * s, 1.6 * s, 8),
      new THREE.MeshStandardMaterial({ color: 0x4a3a2c, roughness: 0.9 }));
    tronco.position.y = 0.8 * s; tronco.castShadow = true; g.add(tronco);
    const hoja = new THREE.MeshStandardMaterial({ color: oscuro ? 0x1f3324 : 0x4f7d45, roughness: 0.9, flatShading: true });
    for (const [dx, dy, dz, r] of [[0, 2.1, 0, 0.95], [0.4, 1.8, 0.2, 0.7], [-0.35, 1.9, -0.25, 0.75], [0.1, 2.6, -0.1, 0.6]]) {
      const b = new THREE.Mesh(new THREE.IcosahedronGeometry(r * s, 1), hoja); b.position.set(dx * s, dy * s, dz * s);
      b.castShadow = true; g.add(b);
    }
    g.position.set(x, 0.15, z); scene.add(g);
  }
  for (const [x, z, s] of [[-12, 7.4, 1.1], [-4, 7.6, 0.9], [9, 7.3, 1.15], [16, -7.4, 1.0], [-17, -7.2, 1.2], [21, 7.5, 0.95]]) arbol(x, z, s);

  const farolas = [];
  function farola(x, z, lado) {
    const g = new THREE.Group();
    const matF = new THREE.MeshStandardMaterial({ color: C.poste, metalness: 0.7, roughness: 0.4 });
    const p = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.09, 5.2, 12), matF); p.position.y = 2.6; p.castShadow = true; g.add(p);
    const brazoF = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.07, 1.4), matF); brazoF.position.set(0, 5.15, -lado * 0.7); g.add(brazoF);
    const cab = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.1, 0.55), matF); cab.position.set(0, 5.1, -lado * 1.35); g.add(cab);
    const lamp = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.02, 0.45), new THREE.MeshStandardMaterial({
      color: 0xfff1d6, emissive: 0xffd9a0, emissiveIntensity: oscuro ? 2.0 : 0.2 }));
    lamp.position.set(0, 5.04, -lado * 1.35); g.add(lamp);
    if (C.farola > 0) {
      const luz = new THREE.PointLight(0xffc78a, C.farola, 16, 1.6); luz.position.set(0, 4.9, -lado * 1.35); g.add(luz);
    }
    g.position.set(x, 0.15, z); scene.add(g); farolas.push(g);
  }
  farola(-8, -5.1, -1); farola(7.5, -5.1, -1); farola(-1, 5.1, 1);

  function textoVentanas(w, h, pisos, cols) {
    const cv = document.createElement("canvas"); cv.width = 256; cv.height = 512; const g = cv.getContext("2d");
    g.fillStyle = oscuro ? "#17191e" : "#c9cbc8"; g.fillRect(0, 0, 256, 512);
    for (let i = 0; i < pisos; i++) for (let j = 0; j < cols; j++) {
      const enc = Math.random() < (oscuro ? 0.42 : 0);
      g.fillStyle = enc ? (Math.random() < 0.5 ? "#ffd59a" : "#fff1d0") : (oscuro ? "#23262d" : "#8fa4b6");
      g.fillRect(12 + j * (232 / cols), 14 + i * (484 / pisos), 232 / cols - 10, 484 / pisos - 12);
    }
    const t = new THREE.CanvasTexture(cv); t.encoding = THREE.sRGBEncoding; return t;
  }
  for (let k = 0; k < 9; k++) {
    const w = 6 + Math.random() * 6, h = 8 + Math.random() * 18, d = 6;
    const tex = textoVentanas(w, h, Math.round(h / 3), Math.round(w / 2));
    const m = new THREE.MeshStandardMaterial({ map: tex, emissiveMap: oscuro ? tex : null, emissive: oscuro ? 0xffffff : 0x000000,
      emissiveIntensity: oscuro ? 0.45 : 0, roughness: 0.8 });
    const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
    b.position.set(-40 + k * 10 + Math.random() * 3, h / 2, -22 - Math.random() * 10); scene.add(b);
  }

  // ---------------------------------------------------------------- espira
  const E = D.espira, s2 = E.lado / 2;
  const matSello = new THREE.MeshStandardMaterial({ color: 0x0c0c0c, roughness: 0.35, metalness: 0.1 });
  const matCable = new THREE.MeshStandardMaterial({ color: C.espira, emissive: C.espira, emissiveIntensity: 1.2 });
  for (const [x, z, lx, lz] of [[0, -s2, E.lado, 0], [0, s2, E.lado, 0], [-s2, 0, 0, E.lado], [s2, 0, 0, E.lado]]) {
    const ranura = new THREE.Mesh(new THREE.BoxGeometry(lx + 0.06 || 0.07, 0.006, lz + 0.06 || 0.07), matSello);
    ranura.position.set(x, 0.003, z); scene.add(ranura);
    const cable = new THREE.Mesh(new THREE.BoxGeometry(lx || 0.018, 0.012, lz || 0.018), matCable);
    cable.position.set(x, 0.005, z); scene.add(cable);
  }
  const conexion = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.006, 3.0), matSello);
  conexion.position.set(s2, 0.003, -s2 - 1.5); scene.add(conexion);

  // ---------------------------------------------------------------- caseta, detector y talanquera
  const xT = 3.4, zT = -5.1;
  const matPoste = new THREE.MeshStandardMaterial({ color: C.poste, metalness: 0.7, roughness: 0.35 });
  const poste = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.25, 16), matPoste);
  poste.position.set(xT - 1.0, 0.78, zT); poste.castShadow = true; scene.add(poste);
  const caja = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.52, 0.22),
    new THREE.MeshStandardMaterial({ color: 0x2a2e35, metalness: 0.4, roughness: 0.45 }));
  caja.position.set(xT - 1.0, 1.6, zT); caja.castShadow = true; scene.add(caja);
  const pcv = document.createElement("canvas"); pcv.width = 256; pcv.height = 300; const pctx = pcv.getContext("2d");
  const ptex = new THREE.CanvasTexture(pcv); ptex.encoding = THREE.sRGBEncoding;
  const pantalla = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.4),
    new THREE.MeshBasicMaterial({ map: ptex, toneMapped: false }));
  pantalla.position.set(xT - 1.0, 1.61, zT + 0.111); scene.add(pantalla);
  const caseta = new THREE.Group();
  const muro = new THREE.MeshStandardMaterial({ color: oscuro ? 0x8a8d92 : 0xe7e6e0, roughness: 0.7 });
  const cuerpoC = new THREE.Mesh(new THREE.BoxGeometry(1.8, 2.3, 1.6), muro); cuerpoC.position.y = 1.15; cuerpoC.castShadow = true; caseta.add(cuerpoC);
  const vent = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.9, 0.02), new THREE.MeshStandardMaterial({
    color: oscuro ? 0xffd59a : 0x9fb6c9, emissive: oscuro ? 0xffc98a : 0x000000, emissiveIntensity: oscuro ? 0.8 : 0, roughness: 0.1 }));
  vent.position.set(0, 1.45, 0.81); caseta.add(vent);
  const techo = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.12, 1.9), matPoste); techo.position.y = 2.36; caseta.add(techo);
  caseta.position.set(xT + 1.8, 0.15, zT - 0.5); scene.add(caseta);
  for (const dz of [0.8, 1.4]) {
    const bol = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.8, 16), new THREE.MeshStandardMaterial({ color: 0xe9b308, roughness: 0.5 }));
    bol.position.set(xT - 0.5, 0.55, zT + dz + 0.6); bol.castShadow = true; scene.add(bol);
  }
  const baseT = new THREE.Mesh(new THREE.BoxGeometry(0.38, 1.05, 0.38), new THREE.MeshStandardMaterial({ color: 0xd9a400, metalness: 0.2, roughness: 0.45 }));
  baseT.position.set(xT, 0.68, zT + 0.95); baseT.castShadow = true; scene.add(baseT);
  const brazo = new THREE.Group(); brazo.position.set(xT, 1.1, zT + 0.95); scene.add(brazo);
  const rcv = document.createElement("canvas"); rcv.width = 512; rcv.height = 16; const rctx = rcv.getContext("2d");
  for (let i = 0; i < 8; i++) { rctx.fillStyle = i % 2 ? "#ffffff" : "#d62828"; rctx.fillRect(i * 64, 0, 64, 16); }
  const rtex = new THREE.CanvasTexture(rcv); rtex.encoding = THREE.sRGBEncoding;
  const largoBrazo = 5.7;
  const barra = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, largoBrazo), new THREE.MeshStandardMaterial({ map: rtex, roughness: 0.4 }));
  barra.position.set(0, 0, largoBrazo / 2); barra.castShadow = true; brazo.add(barra);
  const luzBarra = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 8), new THREE.MeshStandardMaterial({ color: 0xff3b30, emissive: 0xff3b30, emissiveIntensity: 2 }));
  luzBarra.position.set(0, 0.08, largoBrazo - 0.1); brazo.add(luzBarra);

  // ---------------------------------------------------------------- carros
  function monotono(xs, ys) {
    const n = xs.length, d = [], m = new Array(n);
    for (let i = 0; i < n - 1; i++) d.push((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]));
    m[0] = d[0]; m[n - 1] = d[n - 2];
    for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
    for (let i = 0; i < n - 1; i++) {
      if (d[i] === 0) { m[i] = m[i + 1] = 0; continue; }
      const a = m[i] / d[i], b = m[i + 1] / d[i], s = a * a + b * b;
      if (s > 9) { const t = 3 / Math.sqrt(s); m[i] = t * a * d[i]; m[i + 1] = t * b * d[i]; }
    }
    return (u) => {
      if (u <= xs[0]) return ys[0]; if (u >= xs[n - 1]) return ys[n - 1];
      let i = 0; while (u > xs[i + 1]) i++;
      const hh = xs[i + 1] - xs[i], t = (u - xs[i]) / hh, t2 = t * t, t3 = t2 * t;
      return (2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * hh * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * hh * m[i + 1];
    };
  }
  function texturaPlaca(txt) {
    const cv = document.createElement("canvas"); cv.width = 256; cv.height = 80; const g = cv.getContext("2d");
    g.fillStyle = "#f2c200"; g.fillRect(0, 0, 256, 80); g.strokeStyle = "#111"; g.lineWidth = 6; g.strokeRect(3, 3, 250, 74);
    g.fillStyle = "#111"; g.font = "bold 46px Arial"; g.textAlign = "center"; g.fillText(txt, 128, 54);
    g.font = "bold 12px Arial"; g.fillText("CALI", 128, 72);
    const t = new THREE.CanvasTexture(cv); t.encoding = THREE.sRGBEncoding; return t;
  }
  function sombraContacto(L, W) {
    const cv = document.createElement("canvas"); cv.width = cv.height = 128; const g = cv.getContext("2d");
    const gr = g.createRadialGradient(64, 64, 6, 64, 64, 64); gr.addColorStop(0, "rgba(0,0,0,0.75)"); gr.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(L * 1.15, W * 1.35),
      new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(cv), transparent: true, depthWrite: false, opacity: oscuro ? 0.8 : 0.6 }));
    m.rotation.x = -Math.PI / 2; m.position.y = 0.006; return m;
  }

  function rueda(r, lado) {
    const g = new THREE.Group();
    const ancho = 0.165, rin = 0.178;
    const perfil = [[rin, -0.076], [0.232, -0.084], [r - 0.012, -0.079], [r - 0.002, -0.056], [r, -0.02], [r, 0.02],
                    [r - 0.002, 0.056], [r - 0.012, 0.079], [0.232, 0.084], [rin, 0.076]].map(([a, b]) => new THREE.Vector2(a, b));
    const llanta = new THREE.Mesh(new THREE.LatheGeometry(perfil, 48),
      new THREE.MeshStandardMaterial({ color: 0x141414, roughness: 0.88, side: THREE.DoubleSide }));
    llanta.rotation.x = Math.PI / 2; llanta.castShadow = true; g.add(llanta);
    for (let k = 0; k < 36; k++) {
      const surco = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.006, ancho * 0.9), new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 1 }));
      const a = (k / 36) * Math.PI * 2; surco.position.set(Math.cos(a) * (r + 0.001), Math.sin(a) * (r + 0.001), 0);
      surco.rotation.z = a; g.add(surco);
    }
    const metal = new THREE.MeshStandardMaterial({ color: 0xc7cbd1, metalness: 0.95, roughness: 0.22 });
    const barril = new THREE.Mesh(new THREE.CylinderGeometry(rin, rin, ancho - 0.01, 40, 1, true),
      new THREE.MeshStandardMaterial({ color: 0x6f747b, metalness: 0.9, roughness: 0.35, side: THREE.DoubleSide }));
    barril.rotation.x = Math.PI / 2; g.add(barril);
    const cara = new THREE.Shape(); cara.absarc(0, 0, rin - 0.004, 0, Math.PI * 2, false);
    for (let k = 0; k < 5; k++) {
      const a1 = (k / 5) * Math.PI * 2 + 0.33, a2 = a1 + (Math.PI * 2) / 5 - 0.66;
      const hueco = new THREE.Path();
      hueco.moveTo(Math.cos(a1) * 0.155, Math.sin(a1) * 0.155);
      hueco.absarc(0, 0, 0.155, a1, a2, false);
      hueco.lineTo(Math.cos(a2 - 0.22) * 0.065, Math.sin(a2 - 0.22) * 0.065);
      hueco.absarc(0, 0, 0.065, a2 - 0.22, a1 + 0.22, true);
      hueco.lineTo(Math.cos(a1) * 0.155, Math.sin(a1) * 0.155);
      cara.holes.push(hueco);
    }
    const caraG = new THREE.ExtrudeGeometry(cara, { depth: 0.022, bevelEnabled: true, bevelSize: 0.006, bevelThickness: 0.006, bevelSegments: 2, curveSegments: 28 });
    const caraM = new THREE.Mesh(caraG, metal); caraM.position.z = ancho / 2 - 0.045; g.add(caraM);
    const tapa = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.04, 0.03, 20), metal); tapa.rotation.x = Math.PI / 2;
    tapa.position.z = ancho / 2 - 0.012; g.add(tapa);
    const disco = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.014, 32), new THREE.MeshStandardMaterial({ color: 0x8b8f95, metalness: 0.8, roughness: 0.5 }));
    disco.rotation.x = Math.PI / 2; disco.position.z = 0.0; g.add(disco);
    const caliper = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.11, 0.05), new THREE.MeshStandardMaterial({ color: 0x9b1c1c, roughness: 0.5 }));
    caliper.position.set(0.1, 0.06, 0.0); g.add(caliper);
    if (lado < 0) g.scale.z = -1;
    return g;
  }

  function crearCarro(c, estilo) {
    const L = c.largo, W = c.ancho, H = c.alto, h = c.altura_piso, wb = c.entre_ejes, Hb = H - h;
    const r = 0.29, R = r + 0.075, bev = 0.045;
    const x0 = -L / 2, X = (f) => x0 + f * L, Yh = (f) => h + f * Hb;
    const xr = x0 + 0.43 * (L - wb), xf = xr + wb;
    const yl = Yh(estilo.cintura);
    const g = new THREE.Group();
    const pintura = new THREE.MeshPhysicalMaterial({ color: c.color, metalness: 0.3, roughness: 0.3, clearcoat: 1,
      clearcoatRoughness: 0.05, envMapIntensity: 0.55 });
    const vidrio = new THREE.MeshPhysicalMaterial({ color: 0x0a0f14, metalness: 0.25, roughness: 0.05, clearcoat: 1, envMapIntensity: 1.0 });
    const plastico = new THREE.MeshStandardMaterial({ color: 0x1a1b1d, roughness: 0.7 });
    const cromo = new THREE.MeshStandardMaterial({ color: 0xd9dde2, metalness: 1, roughness: 0.15 });
    function extruir(shape, ancho, mat, bevelT) {
      const bt = bevelT === undefined ? bev : bevelT;
      const geo = new THREE.ExtrudeGeometry(shape, { depth: Math.max(0.001, ancho - 2 * bt), bevelEnabled: bt > 0, bevelThickness: bt,
        bevelSize: bt * 0.9, bevelSegments: 5, curveSegments: 24 });
      geo.translate(0, 0, -(ancho - 2 * bt) / 2);
      const m = new THREE.Mesh(geo, mat); m.castShadow = true; m.receiveShadow = true; return m;
    }
    // Deformaciones para que la carrocería no sea una caja: costados abombados, cabina que se angosta hacia el
    // techo (tumblehome) y nariz y cola más angostas vistas desde arriba.
    const plano = (x) => 1 - 0.09 * Math.pow(Math.max(0, (Math.abs(x) - 0.3 * L) / (0.2 * L)), 2);
    const abombado = (y) => 1 - 0.035 * Math.pow((y - Yh(0.42)) / (0.5 * Hb), 2);
    const cabinaF = (y) => 1 - 0.16 * Math.max(0, Math.min(1, (y - yl) / (H - yl)));
    const factor = (x, y) => plano(x) * (y > yl ? cabinaF(y) : abombado(y));
    function deformar(mesh) {
      const P = mesh.geometry.getAttribute("position");
      for (let q = 0; q < P.count; q++) P.setZ(q, P.getZ(q) * factor(P.getX(q) + mesh.position.x, P.getY(q) + mesh.position.y));
      P.needsUpdate = true; mesh.geometry.computeBoundingSphere(); return mesh;
    }
    const zEn = (x, y, z) => z * factor(x, y);
    // --- carrocería baja (perfil lateral con pasos de rueda)
    const al = Math.asin(Math.min(0.99, (r - h) / R));
    const s = new THREE.Shape();
    s.moveTo(X(0.045), h + 0.02);
    s.lineTo(xr - R * Math.cos(al), h + 0.02);
    s.absarc(xr, r, R, Math.PI + al, -al, true);
    s.lineTo(xf - R * Math.cos(al), h + 0.02);
    s.absarc(xf, r, R, Math.PI + al, -al, true);
    s.lineTo(X(0.955), h + 0.02);
    s.quadraticCurveTo(X(0.995), h + 0.02, X(0.998), Yh(0.16));
    s.quadraticCurveTo(X(1.004), Yh(estilo.nariz - 0.12), X(0.99), Yh(estilo.nariz - 0.03));
    s.quadraticCurveTo(X(0.982), Yh(estilo.nariz + 0.02), X(0.955), Yh(estilo.nariz + 0.04));
    s.quadraticCurveTo(X(0.86), Yh(estilo.capo), X(0.72), yl + 0.005);
    s.lineTo(X(0.04), yl + 0.025);
    s.quadraticCurveTo(X(0.0), yl + 0.02, X(0.0), Yh(0.42));
    s.lineTo(X(0.003), Yh(0.14));
    s.quadraticCurveTo(X(0.006), h + 0.02, X(0.045), h + 0.02);
    g.add(deformar(extruir(s, W, pintura)));
    // --- cabina de vidrio (más angosta)
    const Wg = W * estilo.cabina;
    const v = new THREE.Shape();
    v.moveTo(X(0.03), yl - 0.02);
    v.quadraticCurveTo(X(estilo.trasero[0]), Yh(estilo.trasero[1]), X(0.13), H - 0.03);
    v.quadraticCurveTo(X(0.2), H + 0.005, X(0.3), H);
    v.lineTo(X(0.47), H - 0.005);
    v.quadraticCurveTo(X(0.52), H - 0.01, X(0.55), Yh(0.94));
    v.lineTo(X(0.725), yl - 0.02);
    v.lineTo(X(0.03), yl - 0.02);
    g.add(deformar(extruir(v, Wg, vidrio, 0.035)));
    // --- techo pintado sobre la cabina
    const t = new THREE.Shape();
    t.moveTo(X(0.115), H - 0.05);
    t.quadraticCurveTo(X(0.2), H + 0.02, X(0.3), H + 0.018);
    t.lineTo(X(0.47), H + 0.012);
    t.quadraticCurveTo(X(0.53), H + 0.005, X(0.55), H - 0.035);
    t.lineTo(X(0.115), H - 0.05);
    g.add(deformar(extruir(t, Wg + 0.02, pintura, 0.025)));
    // --- pilares pintados a cada lado
    function pilar(pts, lado) {
      const sp = new THREE.Shape(); sp.moveTo(X(pts[0][0]), pts[0][1]);
      for (const [fx, y] of pts.slice(1)) sp.lineTo(X(fx), y);
      const geo = new THREE.ExtrudeGeometry(sp, { depth: 0.014, bevelEnabled: false });
      geo.translate(0, 0, lado > 0 ? Wg / 2 - 0.004 : -Wg / 2 - 0.01);
      g.add(deformar(new THREE.Mesh(geo, pintura)));
    }
    for (const lado of [-1, 1]) {
      pilar([[0.725, yl - 0.02], [0.69, yl - 0.02], [0.528, H - 0.02], [0.552, H - 0.03]], lado);            // A
      pilar([[0.4, yl - 0.02], [0.432, yl - 0.02], [0.428, H - 0.015], [0.398, H - 0.015]], lado);          // B
      pilar([[0.03, yl - 0.02], [0.17, yl - 0.02], [0.2, H - 0.025], [0.13, H - 0.03],
             [X(estilo.trasero[0]) > 0 ? 0.08 : 0.08, Yh(0.85)]], lado);                                     // C
      const tira = new THREE.Mesh(new THREE.BoxGeometry(L * 0.66, 0.022, 0.012), plastico);
      tira.position.set(X(0.37), yl - 0.008, zEn(X(0.37), yl, lado * (Wg / 2 + 0.002))); g.add(tira);
    }
    // --- molduras, parachoques y detalles
    for (const lado of [-1, 1]) {
      const zl = lado * (W / 2 - 0.004);
      const umbral = new THREE.Mesh(new THREE.BoxGeometry(wb - 2 * R + 0.1, 0.07, 0.03), plastico);
      umbral.position.set((xr + xf) / 2, h + 0.05, lado * (W / 2 - 0.03)); g.add(umbral);
      if (estilo.moldura) for (const xw of [xr, xf]) {
        const flare = new THREE.Mesh(new THREE.TorusGeometry(R + 0.01, 0.035, 8, 28, Math.PI - 2 * al + 0.2), plastico);
        flare.rotation.z = -0.1 + al; flare.position.set(xw, r, lado * (W / 2 - 0.035)); flare.scale.z = 0.8; g.add(flare);
      }
      for (const xd of estilo.puertas) {
        const junta = new THREE.Mesh(new THREE.BoxGeometry(0.006, yl - h - 0.12, 0.004), new THREE.MeshBasicMaterial({ color: 0x000000 }));
        junta.position.set(X(xd), (yl + h + 0.1) / 2, zEn(X(xd), (yl + h + 0.1) / 2, lado * (W / 2 + 0.001))); g.add(junta);
      }
      for (const xm of estilo.manijas) {
        const manija = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.025, 0.022), estilo.manijaCromo ? cromo : plastico);
        manija.position.set(X(xm), yl - 0.085, zEn(X(xm), yl - 0.085, zl + lado * 0.006)); g.add(manija);
      }
      const espejo = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 12), pintura);
      espejo.scale.set(0.085, 0.06, 0.06); espejo.position.set(X(0.665), yl + 0.06, lado * (Wg / 2 + 0.09)); espejo.castShadow = true; g.add(espejo);
      const pie = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.03, 0.09), plastico);
      pie.position.set(X(0.675), yl + 0.035, lado * (Wg / 2 + 0.04)); g.add(pie);
      const faro = new THREE.Group();
      const carcasa = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.11, 0.3), cromo);
      const lente = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.085, 0.27), new THREE.MeshStandardMaterial({
        color: 0xf4f7ff, emissive: 0xfff4dc, emissiveIntensity: oscuro ? 1.6 : 0.35, roughness: 0.05 }));
      lente.position.x = 0.028; faro.add(carcasa); faro.add(lente);
      faro.rotation.y = -lado * 0.55; faro.rotation.z = -0.25;
      faro.position.set(X(0.985) + 0.035, Yh(estilo.nariz - 0.06), zEn(X(0.985), Yh(estilo.nariz - 0.06), lado * (W / 2 - 0.26))); g.add(faro);
      const stop = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.24, 0.11), new THREE.MeshStandardMaterial({
        color: 0x9c0f17, emissive: 0xc8101a, emissiveIntensity: oscuro ? 1.2 : 0.35, roughness: 0.15 }));
      stop.position.set(X(0.006), Yh(0.6), zEn(X(0.006), Yh(0.6), lado * (W / 2 - 0.1))); stop.rotation.y = lado * 0.25; g.add(stop);
      const niebla = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.03, 16), cromo);
      niebla.rotation.z = Math.PI / 2; niebla.position.set(X(0.995), Yh(0.2), lado * (W / 2 - 0.25)); g.add(niebla);
    }
    const parrilla = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.09, W * 0.46), plastico);
    parrilla.position.set(X(0.996), Yh(estilo.nariz - 0.1), 0); g.add(parrilla);
    const toma = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.11, W * 0.6), plastico); toma.position.set(X(0.997), Yh(0.27), 0); g.add(toma);
    const labioD = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.05, W * 0.88), plastico); labioD.position.set(X(0.97), h + 0.045, 0); g.add(labioD);
    const labioT = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.07, W * 0.88), plastico); labioT.position.set(X(0.03), h + 0.06, 0); g.add(labioT);
    for (const [xx, rot, yy] of [[X(1.0) + 0.045, Math.PI / 2, Yh(0.27)], [X(0.0) - 0.045, -Math.PI / 2, Yh(0.38)]]) {
      const placa = new THREE.Mesh(new THREE.PlaneGeometry(0.33, 0.11), new THREE.MeshStandardMaterial({ map: texturaPlaca(estilo.placa), roughness: 0.4 }));
      placa.rotation.y = rot; placa.position.set(xx, yy + (rot > 0 ? 0.075 : 0), 0); g.add(placa);
    }
    const ant = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.006, 0.3, 6), plastico);
    ant.position.set(X(0.2), H + 0.14, 0); ant.rotation.z = 0.45; g.add(ant);
    if (estilo.barras) for (const lado of [-1, 1]) {
      const barraT = new THREE.Mesh(new THREE.BoxGeometry(L * 0.36, 0.035, 0.04), plastico);
      barraT.position.set(X(0.33), H + 0.05, lado * (Wg / 2 - 0.06)); g.add(barraT);
      for (const fx of [0.17, 0.49]) {
        const pata = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.05), plastico);
        pata.position.set(X(fx), H + 0.025, lado * (Wg / 2 - 0.06)); g.add(pata);
      }
    }
    const forro = new THREE.MeshStandardMaterial({ color: 0x0b0b0b, roughness: 0.95, side: THREE.DoubleSide });
    for (const xw of [xr, xf]) {
      const a = new THREE.Mesh(new THREE.CylinderGeometry(R - 0.03, R - 0.03, W - 0.1, 28, 1, true, -Math.PI / 2, Math.PI), forro);
      a.rotation.x = Math.PI / 2; a.position.set(xw, r, 0); g.add(a);
    }
    const piso = new THREE.Mesh(new THREE.BoxGeometry(L * 0.82, 0.012, W * 0.86), new THREE.MeshStandardMaterial({ color: 0x2c2e31, metalness: 0.6, roughness: 0.55 }));
    piso.position.set(0, h + 0.012, 0); g.add(piso);
    const ruedas = [];
    for (const x of [xr, xf]) for (const lado of [-1, 1]) {
      const rg = rueda(r, lado), cont = new THREE.Group();
      cont.position.set(x, r, lado * (W / 2 - 0.11)); cont.add(rg); g.add(cont); ruedas.push(rg);
    }
    g.add(sombraContacto(L, W));
    g.userData = { ruedas, r };
    return g;
  }
  const ESTILOS = {
    Spark: { cintura: 0.55, nariz: 0.42, capo: 0.54, cabina: 0.84, trasero: [0.06, 0.86], puertas: [0.2, 0.415, 0.665],
             manijas: [0.3, 0.535], manijaCromo: true, moldura: false, barras: false, placa: "SPK 150" },
    Kwid: { cintura: 0.57, nariz: 0.48, capo: 0.58, cabina: 0.82, trasero: [0.045, 0.88], puertas: [0.2, 0.415, 0.665],
            manijas: [0.3, 0.535], manijaCromo: false, moldura: true, barras: true, placa: "KWD 180" },
  };
  const nombres = Object.keys(D.carros);
  const modelos = {}, lineas = {};
  for (const n of nombres) {
    const c = D.carros[n];
    modelos[n] = crearCarro(c, ESTILOS[c.corto] || ESTILOS.Spark);
    modelos[n].visible = false; scene.add(modelos[n]);
  }

  // ---------------------------------------------------------------- campo magnético
  const fcv = document.createElement("canvas"); fcv.width = 64; fcv.height = 4; const fctx = fcv.getContext("2d");
  const grad = fctx.createLinearGradient(0, 0, 64, 0);
  grad.addColorStop(0, "rgba(255,255,255,0.12)"); grad.addColorStop(0.75, "rgba(255,255,255,1)"); grad.addColorStop(1, "rgba(255,255,255,0.12)");
  fctx.fillStyle = grad; fctx.fillRect(0, 0, 64, 4);
  function grupoLineas(datos, color) {
    const g = new THREE.Group(), tex = new THREE.CanvasTexture(fcv); tex.wrapS = THREE.RepeatWrapping;
    for (const perfil of datos.perfiles) for (const ang of datos.angulos) {
      const pts = perfil.map(([rr, y]) => new THREE.Vector3(rr * Math.cos(ang), y, rr * Math.sin(ang)));
      if (pts.length < 3) continue;
      const curva = new THREE.CatmullRomCurve3(pts), largo = curva.getLength();
      const geo = new THREE.TubeGeometry(curva, Math.max(16, Math.round(largo * 30)), 0.0065, 5, false);
      const m = new THREE.MeshBasicMaterial({ color, map: tex.clone(), transparent: true, opacity: 0.85, depthWrite: false, toneMapped: false });
      m.map.repeat.set(Math.max(1, largo / 0.18), 1); m.map.needsUpdate = true;
      g.add(new THREE.Mesh(geo, m));
    }
    g.userData.mats = g.children.map((ch) => ch.material); scene.add(g); return g;
  }
  const campoVacio = grupoLineas(D.lineas_vacio, C.campo);
  for (const n of nombres) { lineas[n] = grupoLineas(D.carros[n].lineas, C.campo); lineas[n].visible = false; }
  const corr = new THREE.Group(); scene.add(corr);
  const matCorr = new THREE.MeshBasicMaterial({ color: C.corr, transparent: true, opacity: 0, side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false });
  for (const rr of [0.2, 0.34, 0.48, 0.62, 0.74]) {
    const anillo = new THREE.Mesh(new THREE.RingGeometry(rr, rr + 0.022, 72), matCorr); anillo.rotation.x = Math.PI / 2; corr.add(anillo);
  }

  // ---------------------------------------------------------------- brillo (postproceso)
  // Salida directa en sRGB. (El postproceso de brillo de r147 producía franjas en el pavimento.)
  const composer = null;
  renderer.outputEncoding = THREE.sRGBEncoding;
  // halo suave sobre la espira para dar sensación de brillo
  const hcv = document.createElement("canvas"); hcv.width = 64; hcv.height = 64; const hctx = hcv.getContext("2d");
  const hg = hctx.createLinearGradient(0, 0, 0, 64); hg.addColorStop(0, "rgba(255,255,255,0)"); hg.addColorStop(0.5, "rgba(255,255,255,1)");
  hg.addColorStop(1, "rgba(255,255,255,0)"); hctx.fillStyle = hg; hctx.fillRect(0, 0, 64, 64);
  const matHalo = new THREE.MeshBasicMaterial({ color: C.espira, map: new THREE.CanvasTexture(hcv), transparent: true, opacity: oscuro ? 0.55 : 0.3,
    blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false });
  for (const [x, z, lx, lz] of [[0, -s2, E.lado, 0], [0, s2, E.lado, 0], [-s2, 0, 0, E.lado], [s2, 0, 0, E.lado]]) {
    const halo = new THREE.Mesh(new THREE.PlaneGeometry(lx || 0.16, lz || 0.16), matHalo);
    halo.rotation.x = -Math.PI / 2; if (lz) halo.material = matHalo.clone();
    if (lz) { const t = halo.material.map.clone(); t.center.set(0.5, 0.5); t.rotation = Math.PI / 2; t.needsUpdate = true; halo.material.map = t; }
    halo.position.set(x, 0.009, z); scene.add(halo);
  }

  // ---------------------------------------------------------------- etiquetas HTML
  const capa = document.getElementById("labels");
  function etiqueta() { const d = document.createElement("div"); d.className = "lab"; capa.appendChild(d); return d; }
  const L_esp = etiqueta(), L_ch = etiqueta(), L_det = etiqueta(), L_tal = etiqueta(), L_car = etiqueta();
  const v3 = new THREE.Vector3();
  function ubicar(div, x, y, z, dy) {
    v3.set(x, y, z).project(camera);
    const vis = v3.z < 1 && Math.abs(v3.x) < 1.1 && Math.abs(v3.y) < 1.1;
    div.style.display = vis && mostrar.lab ? "block" : "none";
    div.style.left = ((v3.x + 1) / 2 * canvas.clientWidth) + "px";
    div.style.top = ((1 - v3.y) / 2 * canvas.clientHeight - (dy || 16)) + "px";
  }

  // ---------------------------------------------------------------- estado y controles
  const mostrar = { lab: true, campo: true, corr: true };
  let actual = D.carro_inicial in D.carros ? D.carro_inicial : nombres[0];
  let jugando = true, vel = 12 / 3.6, x = -8.5, fase = "llega", espera = 0, angBrazo = 0;
  const btns = document.getElementById("carbtns");
  for (const n of nombres) {
    const b = document.createElement("button"); b.textContent = D.carros[n].corto; b.dataset.n = n;
    b.onclick = () => { actual = n; reiniciar(); marcar(); }; btns.appendChild(b);
  }
  function marcar() { for (const b of btns.children) b.classList.toggle("on", b.dataset.n === actual); }
  function reiniciar() { x = -8.5; fase = "llega"; espera = 0; }
  document.getElementById("play").onclick = (e) => { jugando = !jugando; e.target.textContent = jugando ? "Pausar" : "Reproducir"; };
  document.getElementById("reset").onclick = reiniciar;
  const velIn = document.getElementById("vel"), velV = document.getElementById("velv");
  velIn.oninput = () => { vel = velIn.value / 3.6; velV.textContent = velIn.value + " km/h"; };
  for (const [id, k] of [["tlab", "lab"], ["tcampo", "campo"], ["tcorr", "corr"]]) {
    document.getElementById(id).onclick = (e) => { mostrar[k] = !mostrar[k]; e.target.classList.toggle("on", mostrar[k]); };
  }
  const CAMS = {
    general: { p: [-7.0, 3.6, 7.6], t: [0.7, 0.6, -0.8], polar: 0.495 },
    ras: { p: [3.4, 0.24, 4.4], t: [-0.3, 0.16, 0], polar: 0.5 },
    arriba: { p: [0.4, 13, 0.01], t: [0.4, 0, -0.8], polar: 0.495 },
  };
  let camObj = null;
  for (const b of document.querySelectorAll(".cam")) b.onclick = () => {
    camObj = CAMS[b.dataset.cam]; controls.maxPolarAngle = Math.PI * camObj.polar;
    for (const o of document.querySelectorAll(".cam")) o.classList.toggle("on", o === b);
  };
  camera.position.set(...CAMS.general.p); controls.target.set(...CAMS.general.t);
  // Opciones por URL para capturas: ?x=0&cam=ras&lab=0 (posición fija del carro, cámara y etiquetas)
  try {
    const q = new URLSearchParams(location.search);
    if (q.has("x")) { x = +q.get("x"); fase = "espera"; jugando = false; document.getElementById("play").textContent = "Reproducir"; }
    if (q.has("cam") && CAMS[q.get("cam")]) { const k = CAMS[q.get("cam")]; camera.position.set(...k.p); controls.target.set(...k.t); controls.maxPolarAngle = Math.PI * k.polar; }
    if (q.get("lab") === "0") { mostrar.lab = false; document.getElementById("tlab").classList.remove("on"); }
  } catch (e) { /* sin URL en el iframe de Streamlit */ }
  marcar();

  function interp(c, campo, xx) {
    const xs = c.x, n = xs.length, x0 = xs[0], dx = xs[1] - xs[0];
    const k = (xx - x0) / dx; if (k <= 0) return c[campo][0]; if (k >= n - 1) return c[campo][n - 1];
    const i = Math.floor(k), f = k - i; return c[campo][i] * (1 - f) + c[campo][i + 1] * f;
  }

  // ---------------------------------------------------------------- mini gráfica
  const ch = document.getElementById("chart"), cx = ch.getContext("2d");
  function dibujarGrafica(c) {
    const dpr = Math.min(window.devicePixelRatio, 2), W = 250, H = 110;
    if (ch.width !== W * dpr) { ch.width = W * dpr; ch.height = H * dpr; }
    cx.setTransform(dpr, 0, 0, dpr, 0, 0); cx.clearRect(0, 0, W, H);
    const st = getComputedStyle(document.documentElement);
    const xmin = -6, xmax = 6, ymax = Math.max(...nombres.map((n) => -D.carros[n].dL_max * 100)) * 1.15;
    const X = (v) => 8 + (v - xmin) / (xmax - xmin) * (W - 16), Y = (v) => H - 14 - v / ymax * (H - 26);
    cx.strokeStyle = st.getPropertyValue("--border"); cx.lineWidth = 1;
    cx.beginPath(); cx.moveTo(8, Y(0)); cx.lineTo(W - 8, Y(0)); cx.stroke();
    cx.setLineDash([4, 3]); cx.strokeStyle = st.getPropertyValue("--muted");
    cx.beginPath(); cx.moveTo(8, Y(D.umbral_pct)); cx.lineTo(W - 8, Y(D.umbral_pct)); cx.stroke(); cx.setLineDash([]);
    for (const n of nombres) {
      const cc = D.carros[n]; cx.strokeStyle = cc.color; cx.lineWidth = n === actual ? 2.2 : 1; cx.globalAlpha = n === actual ? 1 : 0.45;
      cx.beginPath(); let first = true;
      for (let i = 0; i < cc.x.length; i++) {
        const xv = cc.x[i]; if (xv < xmin || xv > xmax) continue;
        const px = X(xv), py = Y(-cc.dL_rel[i] * 100); if (first) { cx.moveTo(px, py); first = false; } else cx.lineTo(px, py);
      }
      cx.stroke(); cx.globalAlpha = 1;
    }
    const yv = -interp(c, "dL_rel", x) * 100;
    cx.fillStyle = st.getPropertyValue("--text"); cx.beginPath(); cx.arc(X(Math.max(xmin, Math.min(xmax, x))), Y(yv), 3.5, 0, 7); cx.fill();
    cx.fillStyle = st.getPropertyValue("--muted"); cx.font = "10px Inter, sans-serif";
    cx.fillText("umbral " + D.umbral_pct.toFixed(1) + " %", W - 80, Y(D.umbral_pct) - 4);
    cx.fillText("x (m)", W - 34, H - 2);
  }
  function dibujarPantalla(f, df, txt, on) {
    pctx.fillStyle = "#0f1a14"; pctx.fillRect(0, 0, 256, 300);
    pctx.fillStyle = "#3a4a40"; pctx.fillRect(10, 10, 236, 280);
    pctx.fillStyle = "#0f1a14"; pctx.fillRect(16, 16, 224, 268);
    pctx.fillStyle = "#7dffb0"; pctx.font = "bold 26px monospace"; pctx.fillText("DETECTOR", 30, 54);
    pctx.font = "22px monospace"; pctx.fillText("f  " + f.toFixed(2) + " kHz", 30, 104);
    pctx.fillText("Δf " + (df >= 0 ? "+" : "") + df.toFixed(2) + " kHz", 30, 140);
    pctx.fillStyle = on ? "#7dffb0" : "#4a6a58"; pctx.font = "bold 30px monospace"; pctx.fillText(txt, 30, 214);
    pctx.beginPath(); pctx.arc(206, 50, 12, 0, 7); pctx.fillStyle = on ? "#22e07a" : "#29402f"; pctx.fill();
    ptex.needsUpdate = true;
  }

  // ---------------------------------------------------------------- bucle
  const hx = document.getElementById("hx"), hdl = document.getElementById("hdl"), hf = document.getElementById("hf"),
        hp = document.getElementById("hp"), htxt = document.getElementById("htxt"), est = document.getElementById("estado"),
        hcar = document.getElementById("hcarro");
  const reloj = new THREE.Clock(); let tPant = 0;
  function tamano() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
    if (composer) composer.setSize(w, h);
  }
  window.addEventListener("resize", tamano); tamano();

  function avanzar(dt) {
    const a = 1.6;
    if (fase === "llega") {
      const dFreno = vel * vel / (2 * a);
      const v = x < -dFreno ? vel : Math.sqrt(Math.max(0.04, 2 * a * Math.max(0, -x)));
      x += v * dt; if (x >= 0) { x = 0; fase = "espera"; espera = 0; } return v;
    }
    if (fase === "espera") { espera += dt; if (espera > 2.2) { fase = "sale"; espera = 0; } return 0; }
    if (fase === "sale") { const v = Math.min(vel, 0.3 + 1.4 * espera); espera += dt; x += v * dt; if (x > 9) { fase = "fin"; espera = 0; } return v; }
    espera += dt; if (espera > 1.2) reiniciar(); return 0;
  }

  function cuadro() {
    requestAnimationFrame(cuadro);
    const dt = Math.min(reloj.getDelta(), 0.05), t = reloj.elapsedTime;
    const c = D.carros[actual];
    let v = 0; if (jugando) v = avanzar(dt);
    for (const n of nombres) { modelos[n].visible = n === actual; lineas[n].visible = false; }
    const m = modelos[actual]; m.position.x = x;
    for (const rg of m.userData.ruedas) rg.rotation.z -= v * dt / m.userData.r;

    const dl = interp(c, "dL_rel", x), cob = Math.abs(dl / c.dL_max);
    const fr = E.f0_kHz / Math.sqrt(1 + dl), dfr = fr - E.f0_kHz, pot = interp(c, "potencia_uW", x);
    const detect = -dl * 100 >= D.umbral_pct, reconocido = detect && cob > 0.97;
    const lc = lineas[actual];
    campoVacio.visible = lc.visible = mostrar.campo;
    for (const mm of campoVacio.userData.mats) { mm.opacity = 0.8 * (1 - cob); mm.map.offset.x -= dt * 0.9; }
    for (const mm of lc.userData.mats) { mm.opacity = 0.9 * cob; mm.map.offset.x -= dt * 0.9; }
    matCable.emissiveIntensity = 0.9 + 0.7 * Math.abs(Math.sin(t * 6));
    corr.visible = mostrar.corr; corr.position.set(0, c.altura_piso - 0.004, 0);
    matCorr.opacity = cob * (0.55 + 0.35 * Math.abs(Math.sin(t * 6))); corr.rotation.y += dt * 1.5;
    const abierta = detect || (x > 0 && x < 7.5);
    angBrazo += ((abierta ? 1.45 : 0) - angBrazo) * Math.min(1, dt * 3); brazo.rotation.x = -angBrazo;
    luzBarra.material.emissiveIntensity = abierta ? 0.3 : 1.5 + Math.sin(t * 5);
    if (camObj) {
      const objetivo = new THREE.Vector3(...camObj.p);
      camera.position.lerp(objetivo, 0.08); controls.target.lerp(new THREE.Vector3(...camObj.t), 0.08);
      if (camera.position.distanceTo(objetivo) < 0.02) camObj = null;
    }
    controls.update();
    if (composer) composer.render(); else renderer.render(scene, camera);

    hcar.textContent = actual;
    hx.textContent = (x >= 0 ? "+" : "") + x.toFixed(2) + " m";
    hdl.textContent = (dl * 100).toFixed(2) + " %";
    hf.textContent = fr.toFixed(2) + " kHz";
    hp.textContent = pot.toFixed(1) + " µW";
    est.className = reconocido ? "rec" : (detect ? "on" : "");
    htxt.textContent = reconocido ? `Reconocido: ${D.carros[c.reconocido].corto} (altura estimada ${(c.altura_estimada * 100).toFixed(1)} cm)`
      : (detect ? "Vehículo detectado · talanquera abierta" : "Sin vehículo");
    L_esp.innerHTML = `<b>Espira</b> · ${E.vueltas} vueltas · ${E.L0_uH.toFixed(1)} µH<br><span>${(E.corriente_A * 1000).toFixed(0)} mA a ${E.f0_kHz.toFixed(1)} kHz</span>`;
    L_ch.innerHTML = `<b>Chasis de acero</b> · δ = ${E.delta_acero_mm.toFixed(3)} mm<br><span>absorbe ${pot.toFixed(1)} µW</span>`;
    L_det.innerHTML = `<b>Detector</b><br><span>f = ${fr.toFixed(2)} kHz</span>`;
    L_tal.innerHTML = `<b>Talanquera</b><br><span>${abierta ? "abierta" : "cerrada"}</span>`;
    L_car.innerHTML = `<b>${actual}</b><br>altura al piso ${(c.altura_piso * 100).toFixed(0)} cm · ${c.peso} kg`;
    ubicar(L_esp, -s2, 0, s2, 14);
    ubicar(L_ch, x + c.largo * 0.32, c.altura_piso, c.ancho / 2, 22); if (cob < 0.05) L_ch.style.display = "none";
    ubicar(L_det, xT - 1.0, 1.9, zT, 10);
    ubicar(L_tal, xT, 1.3, zT + 0.95, 10);
    ubicar(L_car, x, c.alto + 0.18, 0, 8);
    if (t - tPant > 0.1) {
      tPant = t; dibujarGrafica(c);
      dibujarPantalla(fr, dfr, reconocido ? D.carros[c.reconocido].corto.toUpperCase() : (detect ? "VEHÍCULO" : "LIBRE"), detect);
    }
  }
  cuadro();
})();
