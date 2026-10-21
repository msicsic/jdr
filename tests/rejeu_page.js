// Fait tourner le script de la page de rejeu (sans navigateur, DOM simulé) : dessine à plusieurs
// instants, avec et sans personnage choisi, tous filtres du journal et options de lumière et de bruit.
// Rend en JSON ce que la page a calculé : degrés de lumière rejoués, ondes dessinées, lignes du journal
// et texte du panneau « ce qu'il entend ». Utilisé par tests/test_rejeu.py.
const fs = require("fs");
const noop = new Proxy(function () {}, { get: (t, k) => k === "measureText" ? () => ({ width: 30 }) : noop, apply: () => noop, set: () => true });
const elements = {};
function el(id) {
  if (!elements[id]) elements[id] = { id, style: {}, checked: true, innerHTML: "", textContent: "", children: [], value: "", hidden: false,
    getContext: () => noop, addEventListener() {}, appendChild(c) { this.children.push(c); if (this.id === "filtre-pnj" && this.value === "") this.value = ""; },
    getBoundingClientRect: () => ({ left: 0, top: 0 }), click() {} };
  return elements[id];
}
global.window = { devicePixelRatio: 1 };
global.document = { getElementById: el, createElement: () => ({ style: {} }), addEventListener() {} };
global.requestAnimationFrame = () => 0;
const page = fs.readFileSync(process.argv[2], "utf-8");
const script = page.match(/<script>([\s\S]*)<\/script>/)[1];
(0, eval)(script + `
const sortie = {lumieres: [], ondes: 0, lignes: {}, ouie: {}, pistes: D.lumiere.length};
const fin = D.fin, pas = Math.max(1, Math.floor(fin / 25));
for (const nature of ["", "ouie", "paroles", "illicite", "voir", "deplacement"]) {
  $("filtre-nature").value = nature; $("filtre-pnj").value = ""; t = fin; choisi = null; dessiner();
  sortie.lignes[nature || "tout"] = ($("lignes").innerHTML.match(/<p /g) || []).length;
}
$("filtre-nature").value = "";
for (let i = 0; i <= 25; i++) {
  t = Math.min(fin, i * pas);
  for (const qui of [null, ...D.personnages]) {
    choisi = qui; $("filtre-pnj").value = qui || ""; dessiner();
    if (qui) sortie.ouie[qui + "@" + t] = $("ouie").innerHTML.length;
  }
  sortie.ondes += bruitsRecents(t).length;
  sortie.lumieres.push(Object.keys(rejouer(D.lumiere, t)).length);
}
console.log(JSON.stringify(sortie));
`);
