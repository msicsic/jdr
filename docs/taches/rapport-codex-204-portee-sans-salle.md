# Lot 204 — portée manuelle au seuil

27 octobre 2026 ; branche `codex-portee-sans-salle`, **non fusionnée**, base
`51c1e0b` vérifiée. Aucun Luna ; deux travailleurs au plus, priorité réduite.
Bruts exclusivement `C:/Users/msics/donjon/artifacts/portee-204/`.

**Invariant en mode cases.** La main suit un pas topologique jusqu'à l'objet,
indépendamment du secteur. Toucher n'exige pas d'entrer dans son volume ou son
support ; murs, autres obstacles, portes et contenants fermés restent bloquants.
Les diagonales exigent les deux côtés libres, comme les pas. Aucun cas de scénario.

`spatial._salle_position` conserve le secteur physique, sans changer les coordonnées
locales du rendu. `contact_cases` appelle `pas_vers` pour `proche`, l'accès PNJ et
son approche ; positions autonomes, attaches et extrémités multiples sont prises
en compte. L'approche garde les positions **crues**, l'exécution contrôle le réel.
`Monde.accessible` admet le contact tactile connu au seuil ; `present_physique`
reste sectoriel. Aucun code de 201/202, du MJ ou du planificateur modifié.

**Preuves.** Saisie réelle torche/crochets du Relais, `antichambre (0,3)` →
`echoppe (8,3)` ; ouverture au seuil de la crypte ; refus des barrières,
coins et distances ; solide, contenant, attache, extrémités, propriété et PNJ.
État complet, regard et inventaire identiques après recharge ; même laps entier
ou découpé avec recharges intermédiaires.

**Tests.** Suite complète unique : **2 385 tests, 276 fichiers, 1 894,12 s,
29 échecs et six erreurs**. Après correction du contact des solides : **88 ciblés
verts**, puis **18 finaux verts**, dont les douze tests du contrat. Bilan consolidé :
**trois échecs préexistants reproduits sur `51c1e0b`** (deux MiMo et l'AST des
accès du compteur 199), zéro erreur ; aucune seconde suite complète.

Adaptations vérifiées des scènes historiques : coup cardinal hors coin de mur ;
prêt réellement allumé avant transmission autonome ; rencontre prouvée par vue
récente plutôt que phrase ; offres uniques par **cause**, un briquet acquis
étant un moyen nouveau. Une empreinte de graphe recalée sur six : −35 états,
−263 successeurs, résultat toujours impossible. L'ancien `_a_portee_de` rétablit
les six captures (`preuve-graphe-contact.json`).

**Bancs.** Empreintes 2 h, quatre scénarios × quatre graines : **6/16 identiques**,
dix écarts de comportement, aucun plantage ; seize références finales en cache.
Relais 1985, 2 h : **VERIFIER + spatial.VERIFICATION = 0,2 verts**.
Banc 4 h, seize paires : **zéro plantage/constat d'usurpation**, pics de passages/h
inchangés (**10/9/18/38**), deux bascules de chaque côté. Retours suspects :

| Scénario | Base → branche |
|---|---:|
| Relais | 1 → 1 |
| Mine | 1 → 2 |
| Auberge | 2 → 5 |
| Crue | 271 → 372 |

Total **275 → 380**, à expliquer **313 → 292**, cycles accomplis **469 → 463**.
Nouvelle alerte `buts_alternes`, Relais 1985 min 5 : Gorm, brasero/garde,
dix alternances ; hausse en crue surtout dans ses familles garder/pulsion/voir.
**Le critère « aucune boucle nouvelle » n'est pas validé : réserve avant intégration
avec le lot 201**, sans modifier ses fichiers ni masquer les alertes.

**Référence.** Sonde incompatible avec `main 812ebe5` (`defense.interposition`
absente, minute zéro). Base exacte `51c1e0b` calculée une fois par configuration,
puis cache `portee-204/references/`. Aucun surcoût déduit des temps du cache.

**Limites.** Sans cases : fonctionnement historique. P2/P3 et M1–M3 restent ouverts ;
aucune garantie générale de stabilité. Aucun brut versionné. Aucune clé de
signature Git configurée : commit non signé.
