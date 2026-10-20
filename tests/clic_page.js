// Fait tourner le script de la page sur un état reçu en entrée (sans navigateur) et rend, en JSON,
// ce que propose un clic sur chaque case, le chemin vers la case connue la plus lointaine, et
// l'approche de chaque chose pour un geste à portée de main, et la commande de chaque flèche. Utilisé par tests/test_web.py.
const fs = require("fs");
const noop = new Proxy(function () {}, { get: (t, k) => k === "measureText" ? () => ({ width: 30 }) : noop, apply: () => noop, set: () => true });
const elements = {};
function el(id) {
  if (!elements[id]) elements[id] = { id, style: {}, checked: false, innerHTML: "", textContent: "", children: [], value: "",
    getContext: () => noop, addEventListener() {}, appendChild(c) { this.children.push(c); }, removeChild() {}, focus() {},
    contains: () => false, getBoundingClientRect: () => ({ left: 0, top: 0 }) };
  return elements[id];
}
global.window = { devicePixelRatio: 1, innerWidth: 1000, innerHeight: 800 };
global.document = { getElementById: el, createElement: () => ({ style: {} }), documentElement: {}, addEventListener() {}, activeElement: null };
global.getComputedStyle = () => ({ getPropertyValue: () => "#333" });
global.EventSource = function () { return {}; };
global.fetch = async () => ({ status: 200 });
global.ETAT = JSON.parse(fs.readFileSync(0, "utf-8"));
const page = fs.readFileSync(process.argv[2], "utf-8");
(0, eval)(page.match(/<script>([\s\S]*)<\/script>/)[1] + `
appliquerEtat(ETAT);
const sortie = {choix: {}, chemin: null, cible: null, approches: {}};
const cases = [...niveau.salles.flatMap(s => s.cases.map(c => c.globale)), ...niveau.sorties.map(s => s.globale)];
cases.forEach(g => {
  const {sections, autres} = choixCase(g);
  const cmds = [...sections.flatMap(x => x[1]), ...autres].map(x => x[2]);
  if (cmds.length) sortie.choix[cle(g)] = cmds;
});
praticables().forEach(k => { const g = k.split(",").map(Number), p = chemin(scene.joueur.globale, g);
  if (p && (!sortie.chemin || p.length > sortie.chemin.length)) { sortie.cible = g; sortie.chemin = p; } });
const approche = g => chemin(scene.joueur.globale, q => Math.max(Math.abs(q[0] - g[0]), Math.abs(q[1] - g[1])) <= 1);
niveau.objets.forEach(o => sortie.approches[o.id] = approche(o.globale));
niveau.sorties.filter(s => s.porte).forEach(s => sortie.approches[s.porte.id] = approche(s.globale));
sortie.fleches = {};
for (const regard of ROSE) {
  scene.joueur.orientation = regard;
  sortie.fleches[regard] = {};
  for (const [nom, ev] of [["gauche", {key: "ArrowLeft"}], ["droite", {key: "ArrowRight"}], ["haut", {key: "ArrowUp"}],
                           ["bas", {key: "ArrowDown"}], ["maj_gauche", {key: "ArrowLeft", shiftKey: true}],
                           ["maj_droite", {key: "ArrowRight", shiftKey: true}], ["alt_haut", {key: "ArrowUp", altKey: true}]])
    sortie.fleches[regard][nom] = commandeFleche(ev);
}
console.log(JSON.stringify(sortie));
`);
