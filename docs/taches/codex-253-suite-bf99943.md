# Tâche Codex 253 : les trois échecs de la suite complète de l'intégration bf99943

Suite complète lancée par le superviseur sur l'intégration `bf99943` (lots 246, 247, 248 fusionnés depuis `bf4cede`,
après les corrections du lot 247) : **2 630 tests, trois échecs**, zéro erreur. Journal recopié dans
`C:\Users\msics\donjon\artifacts\suite-253\suite-bf99943.log`.

1. `test_dynamique_besoins.TenirTests.test_lucien_rapporte_la_lanterne_de_l_etable_au_grenier_au_lieu_d_aller_et_venir` :
   les cinq derniers lieux de Lucien sont `salle_commune` au lieu de `grenier`. **Comportement changé** : il ne rapporte
   plus la lanterne au grenier pour y rester. Suspect principal : le lot 246 (`_rendre` juge la remise sur l'état projeté
   après le trajet), sans certitude.
2. et 3. `test_etapes_chainees.test_captures_mine_et_auberge_memes_plans_visites_monde_et_rendu_recharges`
   (`mine`, `auberge`) : l'empreinte du **monde** diffère (visites et plans non signalés). Suspect principal : le lot 248
   (champ `ascendant` neutre ajouté aux relations, état complet changé par ce seul champ et les empreintes qui en
   dérivent).

Lot de 30 à 45 minutes (`AGENTS.md`, règles du 2026-10-28 : **pas de suite complète**, calculs longs détachés avec
`CALCUL EN COURS : <fichier>`). Pas de Luna. **Poste : le PC fixe**, au plus 2 processus, priorité réduite.

## Ce qu'on attend
- Pour chaque échec, **la fusion qui l'introduit** (entre `bf4cede` après correction, soit `3fbf166`, et `bf99943` :
  `f46a0b5` lot 246, `bf99943` lot 248 ; test vert sur le parent, rouge sur la fusion) et la cause.
- **1 (Lucien)** : défaut à supposer d'abord. Si 246 l'a introduit, dire si le nouveau jugement de la remise est juste
  (la lanterne serait-elle encore nécessaire à Lucien après la remise ? doit-il la rendre ?) ou si la projection d'après
  trajet se trompe ; corriger le contrat commun de `_rendre` ou de son jugement, ou, si le comportement nouveau est juste,
  réancrer l'oracle avec preuve (monde et rendu rechargés, pourquoi l'ancienne attente n'est plus la bonne), sans
  l'affaiblir : l'invariant historique du test (ne pas aller et venir entre la garde et la lumière) doit rester vérifié.
- **2 et 3 (empreintes)** : si seule l'addition du champ neutre et des empreintes qui en dérivent explique l'écart,
  réancrer en le **prouvant** (retirer le champ neutre de la projection comparée, comme le lot 248, et retrouver
  l'ancienne empreinte), pas par simple remplacement du hash.

**Fichiers autorisés d'avance** : les deux fichiers de tests ; `echanges.py` / `planification.py` / `deliberation.py`
pour `_rendre` et son jugement si la cause y est ; leurs tests voisins, arbitrage avec preuve. **Pas** : `social.py`
(lot 250), `agendas.py` (lot 252), le MJ, les scénarios.

## Vérification
- Les trois tests verts, plus les fichiers voisins des fonctions modifiées.
- Si du code moteur change : banc rapide 4 h, cinq scénarios × quatre graines, référence `bf99943` du cache, lancé
  détaché ; suspects sans hausse.
- Pas de suite complète.

## Livraison
- Branche `codex-suite-bf99943` poussée. Rapport d'une page `docs/taches/rapport-codex-253-suite-bf99943.md` ; entrée
  « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\suite-253\`. Termine par
  `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
