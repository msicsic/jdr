# Lot 402 — Vérification d'intégration

31 octobre 2026, PC fixe `MSI-DESKTOP`, branche `codex-verif-integ-4`.
Code figé sur **`4539dd68afab91eda07aa7561045c09d39e6ba5e`**.
**Calcul en cours : aucun verdict d'intégration à ce stade.**

Bruts : `C:/Users/msics/donjon/artifacts/verif-integ-4539dd68/`.
Le lanceur détaché `campagnes.py` exécute une seule nuit à la fois, à priorité
réduite ; `campagnes.pid`, `campagnes.log` et `PROGRESSION.json` permettent
de retrouver le processus et sa progression. `FIN.json` est écrit en dernier.
Aucun changement de `donjon/` ou `tools/`, aucun pull, appel Luna ou lancement
de suite complète. Les empreintes des sources sont consignées dans
`MANIFESTE.json` et contrôlées à la fin.

Les 49 nuits reprennent les conditions du lot 274 : départ tiré ; audit
12 h, Relais/mine/auberge/crue, graines 1985/7/42/2024/3/11/99/500 ; rixe et
rixe douce 8 h, quatre premières graines ; `VERIFIER` et vérification spatiale
0,2 sur 8 h, graine 42, Relais/mine/auberge/crue/rixe ; hameau 12 h,
quatre premières graines. La salle passive de `rixe_douce` est renseignée
dans le lanceur externe, comme au lot 274, sans modifier l'outil versionné.
Les classes 219 et causes 227 sont actives dans leur version de départ.

Les 49 archives de `verif-integ-0bad227/` servent de référence, uniquement
en lecture. Le lanceur produit les analyses par campagne pour les deux
versions et `resume-comparatif.json`, sans rejouer de nuit de référence.
Les états complets finaux actuels sont aussi archivés dans `etats-finaux/`.

**À compléter après `FIN.json` :** tableau des moyennes `0bad227` → `4539dd68`
(mesures du 274, 219/227 et S/F/D), plantages, violations, usurpations, coups,
morts, captivité, écarts de contrôle et recherches bornées ; appels et passages
après 374 (Aubin crue 42 et auberge/mine/crue), richesse et attente du hameau,
dettes/remboursements et mandats A5. Chaque défaut nouveau devra identifier
son cas réel et l'invariant en cause ; toute boucle sera comparée à la même
nuit de référence. Les changements des compteurs seront distingués des
changements de comportement ; cette comparaison groupée ne permet pas
d'attribuer à S1 seul un écart entre les deux intégrations.
