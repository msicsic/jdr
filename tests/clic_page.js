// Fait tourner le script de la page sur un état reçu en entrée (sans navigateur) et rend, en JSON,
// ce que propose un clic sur chaque case, le chemin vers la case connue la plus lointaine (et vers des buts donnés), et
// l'approche de chaque chose pour un geste à portée de main, et la commande de chaque flèche. Utilisé par tests/test_web.py.
const fs = require("fs");
const noop = new Proxy(function () {}, { get: (t, k) => k === "measureText" ? () => ({ width: 30 }) : noop, apply: () => noop, set: () => true });
const elements = {};
function el(id) {
  if (!elements[id]) elements[id] = { id, style: {}, checked: false, innerHTML: "", textContent: "", children: [], value: "",
    getContext: () => noop, addEventListener() {}, appendChild(c) { this.children.push(c); }, removeChild() {}, focus() {},
    contains: () => false, getBoundingClientRect: () => ({ left: 0, top: 0 }) };
  if (!Object.getOwnPropertyDescriptor(elements[id], "innerHTML").set) {
    Object.defineProperty(elements[id], "innerHTML", {get() { return this.html || ""; },
      set(v) { this.html = v; this.children = []; }});
  }
  return elements[id];
}
let numeroElement = 0;
global.window = { devicePixelRatio: 1, innerWidth: 1000, innerHeight: 800 };
const ecouteurs = global.ecouteurs = {};
global.document = { getElementById: el, createElement: tag => Object.assign(el("nouveau-" + (++numeroElement)), {tagName: tag.toUpperCase()}), documentElement: {}, activeElement: null,
  addEventListener(type, f) { (ecouteurs[type] = ecouteurs[type] || []).push(f); } };
global.getComputedStyle = () => ({ getPropertyValue: () => "#333" });
global.EventSource = function () { return {}; };
global.requestAnimationFrame = () => 0;
const envois = global.envois = [];
global.fetch = async (url, options) => { if (url === "/commande") envois.push(JSON.parse(options.body).descripteur || JSON.parse(options.body).texte); return { status: 200 }; };
global.ETAT = JSON.parse(fs.readFileSync(0, "utf-8"));
const page = fs.readFileSync(process.argv[2], "utf-8");
(0, eval)(page.match(/<script>([\s\S]*)<\/script>/)[1] + `
appliquerEtat(ETAT);
const sortie = {choix: {}, envoisClic: [], outils: [], chemin: null, cible: null, approches: {}};
sortie.corps = [];
sortie.inventaire = [];
for (const li of $("inventaire").children) {
  const bouton = li.children[0];
  if (!bouton) continue;
  occupe = false;
  bouton.onclick({clientX: 10, clientY: 10, stopPropagation() {}});
  const choix = $("menu").children.filter(b => b.onclick);
  for (const b of choix) {
    occupe = false; envois.length = 0;
    b.onclick();
    if (envois.length) sortie.inventaire.push({bien: bouton.textContent, libelle: b.textContent, envoye: envois[0], clics: 2});
    else for (const p of $("menu").children.filter(b => b.onclick)) {
      occupe = false; envois.length = 0; p.onclick();
      if (envois.length) sortie.inventaire.push({bien: bouton.textContent, libelle: b.textContent, destinataire: p.textContent, envoye: envois[0], clics: 3});
    }
  }
}
if (niveau) {
// Les objets ancrés à un mur sont cliquables aussi : leur case n'est pas un sol.
const cases = [...niveau.salles.flatMap(s => s.cases.map(c => c.globale)),
  ...niveau.sorties.map(s => s.globale), ...niveau.objets.map(o => o.globale), ...niveau.echelles.map(e => e.globale)];
cases.forEach(g => {
  const {sections, autres} = choixCase(g);
  const cmds = [...sections.flatMap(x => x[1]), ...autres].map(x => x[2]).filter(x => x !== undefined);
  if (cmds.length) sortie.choix[cle(g)] = cmds;
  // Exécuter les vrais callbacks de chaque geste et regarder le corps HTTP.
  const origine = scene.joueur.globale;
  scene.joueur.globale = g;  // Déjà à portée : l'approche est sondée séparément.
  for (const choix of sections.flatMap(x => x[1])) {
    if (choix[3] === "corps") continue; // Arbre de méthodes/moyens sondé ci-dessous.
    occupe = false; envois.length = 0;
    choix[1]();
    if (choix[2] !== undefined) sortie.envoisClic.push({choix: choix[2], envoye: envois[0], clics: 2});
    else for (const p of $("menu").children.filter(b => b.onclick)) {
      occupe = false; envois.length = 0; p.onclick();
      if (envois.length) sortie.outils.push({libelle: choix[0], ressource: p.textContent, envoye: envois[0], clics: 3});
    }
  }
  scene.joueur.globale = origine;
});
for (const o of niveau.objets) {
  const origine = scene.joueur.globale;
  scene.joueur.globale = o.globale;
  const parcourir = (b, chemin) => {
    occupe = false; envois.length = 0; b[1]();
    if (envois.length) sortie.corps.push({cible: o.id, choix: chemin, envoye: envois[0], clics: chemin.length + 1});
    else for (const bouton of $("menu").children.filter(b => b.onclick))
      parcourir([bouton.textContent, bouton.onclick], [...chemin, bouton.textContent]);
  };
  choixCorps(o, 10, 10).forEach(b => parcourir(b, [b[0]]));
  scene.joueur.globale = origine;
}
praticables().forEach(k => { const g = k.split(",").map(Number), p = chemin(scene.joueur.globale, g);
  if (p && (!sortie.chemin || p.length > sortie.chemin.length)) { sortie.cible = g; sortie.chemin = p; } });
// Avec sonde_buts (cases globales), le chemin de la page jusqu'à la première qu'elle juge la plus rapide.
if (ETAT.sonde_buts) sortie.vers_buts = chemin(scene.joueur.globale, q => ETAT.sonde_buts.some(b => cle(b) === cle(q)));
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
// Espace selon ce qui a le focus : la commande envoyée, et si l'espace est gardée.
sortie.espace = {};
$("commande").tagName = "INPUT";
for (const [nom, actif, valeur] of [["saisie_vide", $("commande"), ""], ["saisie_ecrite", $("commande"), "je"],
                                     ["carte", $("carte-cadre"), ""], ["bouton", {tagName: "BUTTON"}, ""]]) {
  occupe = false; envois.length = 0; document.activeElement = actif; $("commande").value = valeur;
  let empeche = false;
  ecouteurs.keydown.forEach(f => f({key: " ", preventDefault() { empeche = true; }}));
  sortie.espace[nom] = {envoi: envois[0] || null, empeche};
}
}
if (ETAT.sonde_fabrication) {
  appliquerEtat(ETAT); occupe = false; envois.length = 0;
  $("fabriquer").onclick({clientX: 10, clientY: 10, stopPropagation() {}});
  const offres = $("menu").children.filter(b => b.onclick);
  sortie.fabrication = {offres: offres.map(b => b.textContent), champs: [], clics: 2};
  const f = ETAT.sonde_fabrication;
  const b = offres[f.index || 0];
  if (b) {
    b.onclick();
    const form = $("fabrication");
    form.onsubmit({preventDefault() {}});
    sortie.fabrication.incomplet = envois.length;
    for (const label of form.children.filter(l => l.tagName === "LABEL")) {
      const input = label.children.find(c => ["INPUT", "SELECT"].includes(c.tagName));
      const nom = label.children[0].textContent;
      const choix = input.children.map(o => ({valeur: o.value, texte: o.textContent}));
      input.value = String(f.valeurs[nom] ?? "");
      if (input.tagName === "SELECT" && !choix.some(o => o.valeur === input.value)) throw Error("Choix absent : " + nom + " / " + input.value);
      if (input.onchange) input.onchange();
      document.activeElement = input;
      for (const key of ["ArrowUp", "ArrowDown", " "]) ecouteurs.keydown.forEach(cb => cb({key, preventDefault() {}}));
      sortie.fabrication.champs.push({nom, choix, valeur: input.value, detail: label.children[2]?.textContent || ""});
      sortie.fabrication.clics += input.tagName === "SELECT" ? 2 : 1;
    }
    sortie.fabrication.clavier = envois.length;
    document.activeElement = null;
    occupe = true; form.onsubmit({preventDefault() {}});
    sortie.fabrication.occupe = envois.length;
    occupe = false; form.onsubmit({preventDefault() {}});
    sortie.fabrication.clics++;
    sortie.fabrication.envoye = envois[0];
    form.onsubmit({preventDefault() {}});
    sortie.fabrication.envois = envois.length;
    appliquerEtat(ETAT);
    sortie.fabrication.ferme_apres_etat = form.hidden;
  }
}
if (ETAT.sonde_information) {
  appliquerEtat(ETAT); occupe = false; envois.length = 0;
  $("informer").onclick();
  const form = $("information"), f = ETAT.sonde_information;
  sortie.information = {champs: [], clics: 1};
  form.onsubmit({preventDefault() {}});
  sortie.information.incomplet = envois.length;
  const remplir = label => {
    const input = label.children.find(c => c.tagName === "SELECT");
    const nom = label.children[0].textContent;
    const choix = input.children.map(o => ({valeur: o.value, texte: o.textContent}));
    input.value = f[nom] || "";
    if (!choix.some(o => o.valeur === input.value)) throw Error("Choix absent : " + nom + " / " + input.value);
    if (input.onchange) input.onchange();
    document.activeElement = input;
    for (const key of ["ArrowUp", "ArrowDown", " "]) ecouteurs.keydown.forEach(cb => cb({key, preventDefault() {}}));
    sortie.information.champs.push({nom, choix, valeur: input.value});
    sortie.information.clics += 2;
  };
  form.children.filter(l => l.tagName === "LABEL").forEach(remplir);
  form.children.filter(l => l.tagName === "DIV").flatMap(l => l.children).forEach(remplir);
  sortie.information.clavier = envois.length;
  document.activeElement = null;
  occupe = true; form.onsubmit({preventDefault() {}});
  sortie.information.occupe = envois.length;
  occupe = false; form.onsubmit({preventDefault() {}});
  sortie.information.clics++;
  sortie.information.envoye = envois[0];
  form.onsubmit({preventDefault() {}});
  sortie.information.envois = envois.length;
  appliquerEtat(ETAT);
  sortie.information.ferme_apres_etat = form.hidden;
}
if (ETAT.sonde_marche) {
  appliquerEtat(ETAT);
  envois.length = 0; occupe = false;
  allerA(ETAT.sonde_marche.cible);
  for (const suivant of ETAT.sonde_marche.etats) {
    appliquerEtat(suivant); occupe = false; poursuivre();
  }
  sortie.marche = {envois: [...envois], interrompue: marche === null};
}
console.log(JSON.stringify(sortie));
`);
