# Lot 38 — coût des nuits de 12 h, mêmes décisions

Branche `codex-cout-12h`, non fusionnée ; moteur de référence `63a717c`, ancien moteur
`42bb9c0`. Aucun appel au modèle, aucun coût, prix, plafond ou scénario modifié ; `main` inchangé.

**Hypothèse confirmée en partie.** Sur les reprises à 8 h, graine 1985, la mine et l'auberge
développent 10 049 / 10 408 états en cinq minutes de jeu, avec 6–7 déplacements candidats par
état. Mais 94–99 % ont déjà des faits de préparation : l'inventaire et les effets combinés
comptent aussi, pas seulement les déplacements bon marché avant la demande. Les parts remises
occupent 33 / 42 % du profil initial, dont les devis 20 / 17 %.

**Trois leviers.** Borne A* sur les suites terminales, rang historique réservé, normalisation
commune ; h = 0 sur les états ordinaires. Une suite inconnue reste une lacune du certificat,
jamais une preuve d'absence. Puis caches exacts des parts, besoins de combustible, attentes et
devis ; enfin références des imports chauds gardées. Admissibilité, cohérence, découverte de
lumière, graphes et clés : `docs/plan-planificateur.md`.

Mesure séparée : quatre versions lancées ensemble, priorité réduite, une nuit à la fois par
version ; 12 h, graine 1985. Chaque ligne ajoute seulement le levier indiqué à la précédente :

| Version | Mine, CPU (s) | Auberge, CPU (s) | Gain mine / auberge contre la ligne précédente |
|---|---:|---:|---|
| Base | 338,67 | 224,34 | — |
| + borne terminale | 325,52 | 224,42 | 3,88 % / −0,04 % |
| + caches exacts | 319,38 | 219,61 | 1,89 % / 2,14 % |
| + imports gardés | 269,47 | 193,11 | 15,63 % / 12,07 % |

Les trois étapes conservent aussi tous les résultats de recherche des deux nuits.

Mesure principale : ancien/base/branche **lancés ensemble**, deux processus chacun. Dans
chaque cellule : **ancien / base / branche**, secondes CPU ; les tranches viennent des relevés
à 240, 480 et 720 minutes (`empreintes_nuits.py`, désormais `cpu_cumule_4h`).

| Nuit | Total | 0–4 h | 4–8 h | 8–12 h |
|---|---|---|---|---|
| Mine 42 | 87,98 / 266,08 / 210,36 | 8,16 / 9,70 / 9,17 | 15,34 / 49,17 / 40,72 | 64,44 / 207,14 / 160,44 |
| Mine 1985 | 77,47 / 357,16 / 287,03 | 7,33 / 8,67 / 8,30 | 19,59 / 117,72 / 91,09 | 50,47 / 230,70 / 187,58 |
| Auberge 42 | 78,16 / 312,97 / 260,98 | 6,25 / 8,75 / 8,38 | 11,61 / 28,50 / 24,91 | 60,20 / 275,64 / 227,61 |
| Auberge 1985 | 71,84 / 236,78 / 203,25 | 6,00 / 7,97 / 7,64 | 12,30 / 33,55 / 28,91 | 53,50 / 195,17 / 166,61 |

**Identité sur le périmètre demandé.** Quatre nuits longues : `comparer --calcul`, zéro différence
de monde, chronique, mesures, récit, souvenirs, repères et résultats de recherche complets.
Mêmes nœuds et recherches bornées :
mine 1 599 108 / 2 194 545 et 272 / 471 ; auberge 990 823 / 680 203 et 8 / 1 (42 / 1985).
Empreintes 2 h, quatre scénarios × quatre graines : identiques. `VERIFIER` et
`spatial.VERIFICATION=1`, 2 h, mine/auberge 42 : zéro écart, zéro borne. Cinq tests nouveaux
contrôlent moins d'états internes de devis, même plan, état et rendu après recharge, égalités,
plafond, filtres, cache et certificat. Les deux vraies captures à 8 h sont aussi rechargées,
vécues cinq minutes et comparées avec l'évaluation immédiate, état et rendu compris.
Suite unique : **1 707 tests, 4 ignorés, aucun échec**,
688,6 s, trois processus ; les cinq ciblés renforcés repassent ensuite.

**Visée ×1,5 non atteinte.** Gain moyen contre la base : **20,2 % mine, 15,6 % auberge** ;
encore **×3,01 / ×3,09** contre l'ancien moteur. Profil final à 8 h : exploration 94–96 %,
approches 26 %, devis 18 %, imports moins de 1 % (parts cumulatives non additives).
La borne économise des états de devis ; l'heuristique positive des millions d'états ordinaires
reste ouverte. Recherches bornées et approximation du devis inchangées ; aucun retrait d'états
dominés ni élargissement du lot pour forcer la cible. Pic mémoire final : 119 Mo mine,
185 Mo auberge, contre 114 / 175 pour la base.

Commits de code signés SSH : `408499b`, `a304a11`, `66a06cd`. Bruts et entrées des ablations
(empreintes, traces condensées, tranches, profils, patches et SHA-256) : `artifacts/codex-38/`
du worktree ; rapport, plan, point de reprise et deux captures de test versionnés avec le code.
