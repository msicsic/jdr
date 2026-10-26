# Tâche Codex 118 (coût) : ne plus jeter ce que la recherche peut garder — pistes A1 à A4 de la revue Argon

Lot de coût **exact** (mêmes décisions, `comparer --calcul` identique). Pas de Luna. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul ; le lot 119
(perception : `pnj.py`, `esprits.py`, `signes.py`) tourne en même temps : ce lot reste dans `planification.py` (et `trajet_estime.py`
si besoin). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Seuil de l'utilisateur** pour avancer `main` : auberge 1985, 12 h, CPU ≤ ×1,5 contre `42bb9c0`, départ fixe **et** tiré.
Aujourd'hui (lot 114) : ×1,65 / ×2,64. Lis `AGENTS.md`, la revue `docs/taches/rapport-revue-argon-cout.md` et son brief
`docs/taches/revue-argon-cout.md`, les rapports des lots 71, 81, 87, 92 c, 98, 105, 109, puis `donjon/planification.py`
(`vues_du_choix`, `vue`, `_entrees_communes`, `chercher`, `_explorer`, `_explorer_etats`, `_normaliser_suites`, `gestes`,
`_sans_plan`, `_GRAPHES`, `_MEMOIRE`, `_IMPOSSIBLES`).

## Quatre leviers, un commit et une mesure chacun, dans cet ordre
- **A3 — tables d'un même choix partagées** : les tables qui ne dépendent que du monde cru (`_routes`, `_allers`, `_approches`,
  `_contacts`, `_locaux`, `_moyennes`, `_parcours`, `_pressions`, tarifs, droits…) et `_entrees_communes` (et son `json.dumps`) sont
  calculées une fois par `vues_du_choix`, partagées par les candidats d'un même `choisir` comme `_verifier` et
  `_preparer_graphe_preuve` le font déjà ; chaque recherche garde ses paramètres et découvertes propres.
- **A2 — clé commune sans lectures mortes** : `_entrees_communes` ne contient que ce que la recherche lit. Établis-le fonction par
  fonction : les positions crues (`"cases"`) seulement des objets/personnes que la recherche lit à la case (cibles de la salle de
  départ, donneurs de part…) ; `signes.actives` seulement si un appelant sous `chercher` les lit (la fusion de 3c les y avait mis
  pour `menaces` : vérifie s'il est hors recherche). Toute lecture retirée à tort doit faire échouer `VERIFIER`.
- **A1 — garder dès la première recherche** : le graphe repris (`sombre`/`lumiere`) est conservé entre les passes internes dès le
  premier appel (découverte de lumière, de discrétion), la marque `discretion` est retenue par PNJ et but, et le certificat
  `_sans_plan` est établi dès le premier épuisement au lieu d'attendre une seconde recherche identique ; mêmes plans, coûts,
  ordres. Mesure le coût mémoire.
- **A4 — `gestes` une fois par état sans allure** : `gestes(v, e, …)` ne lit pas `e.allure` ; les deux allures partagent sa liste
  (le filtre d'allure reste dans `_normaliser_suites`) ; et, **hors plafond seulement**, un état `allure=30` non furtif à la
  dernière profondeur n'empile pas de feuilles qui ne peuvent ni conclure ni être développées. Si ce second point peut changer une
  recherche bornée, garde-le dans le contrat des lots 46/48 (sinon retire-le).

## Vérification
- Pour **chaque** levier : captures auberge 1985 à 480 et 600 min et mine à 480 (lots 81/86/105) : mêmes états, successeurs
  ordonnés, coûts hexadécimaux et plans ; monde et rendu après recharge.
- À la fin : empreintes 2 h, quatre scénarios × quatre graines (référence en cache) ; `VERIFIER` + `spatial.VERIFICATION=1`, auberge
  42 tirée, 2 h ; CPU 12 h auberge 1985 fixe et tiré (et mine 1985 fixe) par paires lancées ensemble (`42bb9c0`/branche,
  base/branche), deux processus, tranche 8–12 h, `comparer --calcul` mêmes résultats ; mémoire de pointe ; suite complète une
  fois (`tools/tests.py --processus 2`). Dis où cela place l'auberge contre ×1,5, et le gain de chaque levier.
- **Méfiance envers `cProfile`** (il grossit les petits appels, revue Argon) : décide sur le CPU nu des paires.

## Livraison
Commits signés (un par levier), branche poussée (pas `main`). `docs/plan-planificateur.md`, `docs/etat-dev.md` (« Branche
`codex-reprises-exactes`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-118-reprises-exactes.md`.
