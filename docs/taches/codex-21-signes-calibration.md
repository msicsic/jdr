# Tâche Codex 21 : les signes (3c), coût, relectures, calibration, « observer » dans le noir

Branche `codex-signes-calibration` (elle porte ce fichier, issue de `main` 8855312), worktree dans `tmp-worktrees/`.
Lis d'abord `AGENTS.md`, `docs/etat-dev.md` (entrée `codex-relations-3c` et sa fusion, « À revoir » : Relations 3c),
`docs/plan-relations.md` (§ 6, la lecture des signes, et le critère de 3c), le
[rapport de la tâche 11](rapport-codex-11-relations-3c.md) (mesures, grille proposée), puis `donjon/signes.py`
(`lire`, `percevoir_tous`, `de`, `percus`, `actives`, `impressions`, `mesures`), `relations._lecture`,
`spatial.etat_signes`, `tools/audit_nuits.py`.

**Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt principal, copies seulement).

Un autre lot tourne en même temps (Q, trajets réels : `planification.py`, `obstacles.py`, `part_estimee.py`,
`defense.py`, `pnj._marcher`). **Ne touche ni `planification.py` ni `deliberation.py`** ; si un invariant
l'exige vraiment, change le minimum, isole-le dans un commit à part et dis-le dans le rapport.

## Le constat
Fusionné après H, 3c n'a pas atteint son critère :
- **Méprises** : 824 sur 1 995 lectures par défaut (41,3 %) ; justesse 0,48 à 0,62 aux PSY ordinaires (10–12),
  0,8 seulement pour Gorm à PSY 16, Hugues à 16 : 0,63. Critère du plan : au moins 0,8 à PSY ≥ 13, au plus 0,6 à
  PSY ≤ 9, moins d'une méprise sur cinq lectures retenues. La règle (manqué de 1 à 5 : rien ; au-delà : méprise)
  n'est pas en cause en soi : le cumul pénombre −4, distance −2 et dissimulation `mod + 5` rend les échecs
  profonds fréquents, surtout pour les intentions.
- **Coût** : depuis H, une nuit coûte au processeur mine +35 %, autres +10 à +15 % (`percevoir_tous` émet les
  signes de tous puis fait lire chaque PNJ, aux minutes et aux événements ; la clé sociale et les lectures
  d'axes, `relations._lecture`, sont recalculées pour tous).
- **Relectures** : un même signe se relit toutes les dix minutes ; un guet relu redevient une nouvelle
  `intention_lue` (mine : confidences 0,75 → 9,25 par nuit, les guets lus redits) ; les lignes « Lecture de … »
  relues font les alertes `repetition` de l'audit.
- **« observer » dans le noir** : « observer Ilse », Ilse connue mais invisible, est refusé par l'analyse locale
  avec « Tu ne vois pas cet objet ici » ; en ligne, ce refus part au MJ (`jeu.py` : une intention libre peut
  dépasser la syntaxe locale) : 4 à 5 appels et 1 à 2 refus avant une réponse juste (banc `signes-noir`), au
  lieu de 0.
- **Vols vus** en baisse à la mine, l'auberge et la crue dans le banc de 3c, sans preuve que ce soit la
  dissuasion par les guets lus.

## Les invariants, dans cet ordre (un commit au moins par étape)
1. **Coût, sans rien changer** : les signes émis et lus ne se recalculent que pour ce qui a changé (personnage
   dont l'état, l'intention, la relation ou l'émotion a changé ; observateur dont la perception a changé),
   sous des clés qui disent ce qu'elles lisent. Preuve : empreintes identiques à 8855312
   (`tools/comparer_bancs.py --empreintes`, 2 h puis 8 h, quatre scénarios et `rixe` × 4 graines),
   `spatial.VERIFICATION` recompare chaque lecture gardée à son calcul pur. Temps mesuré (`main` et la branche
   lancés ensemble, `tools/empreintes_nuits.py`) : vise un surcoût des signes d'au plus +15 % par rapport à
   `main` 276524c (avant H) à la mine ; dis ce qui reste et où (profil).
2. **Relire n'est pas apprendre de nouveau** : une relecture qui conclut comme la lecture active la rafraîchit
   (date, confiance) sans nouveau souvenir, nouvelle, confidence ni ligne « Lecture » nouvelle pour l'audit ;
   un échec ne défait pas une lecture active ; une lecture qui change (autre sens, signe disparu puis revenu,
   lecture périmée) compte comme nouvelle. Même règle pour le joueur (`observer` ne répète pas une impression)
   et pour les PNJ. Mesure : alertes `repetition`, confidences et intentions lues à la mine, avant → après,
   chaque écart expliqué par une nuit lue.
3. **Calibration commune** : mesure une grille commune à tous (au moins pénombre −4/−3/−2, dissimulation
   +5/+4/+3, et la largeur de la bande « rien », 5 ou plus), sans réglage par personnage ni par scénario ;
   contrôle ensemble justesse haute, justesse basse, part des méprises et taux d'abstention (« rien »), par
   sorte de signe (place, regard, expression, ton, durée). Lecteurs réglés (`banc_pnj --regler`) : Gorm au
   Relais et Hugues à l'auberge, PSY 8, 11, 14, 16, 4 graines, 8 h ; plus les nuits par défaut des quatre
   scénarios. Retiens le réglage qui atteint le critère du plan, ou, s'il n'existe pas, le meilleur compromis
   avec ses chiffres et la raison. Ne change pas la règle de lecture elle-même (jet, bande, sens d'une méprise,
   « fatigue » pour qui dissimule) sans le proposer d'abord dans le rapport.
4. **« observer » une personne connue qu'on ne voit pas** : le refus vient du moteur, une cause, avec ce qui
   manque (la lumière, la vue, la présence), « cette personne » et non « cet objet » ; il est montré au joueur
   sans appel au MJ, en ligne comme hors ligne, comme les autres refus locaux d'une perception. Cas réel
   `signes-noir` et un autre de même nature (personne connue hors de vue, dans une autre salle).
5. **Vols vus** : à la mine, lis deux nuits où un vol tenté n'est pas vu avec les signes et l'est sans (ou
   l'inverse) et dis si c'est la dissuasion par un guet lu ; aucune correction demandée, seulement le constat.

## Vérifications
- Tests après rechargement (`tests/test_signes.py`, ou un fichier nouveau) : chaque invariant avec son cas réel
  et un autre de même nature ; une relecture sans nouveau souvenir ; un échec qui ne défait pas une lecture ;
  `observer` dans le noir, local, sans appel ; même laps d'un bloc ou découpé.
- Suite complète verte (`tools/tests.py --processus 3`).
- `planification.VERIFIER` et `spatial.VERIFICATION` 1 sur 2 h, puis 0,2 sur 8 h graine 42, chaque scénario et
  `rixe`, sans écart.
- Banc rapide après les étapes 2 à 4 (`comparer_bancs`, 4 h, 4 graines, quatre scénarios, contre 8855312) :
  aucune usurpation, violation ni boucle nouvelle (`tools/audit_nuits.py`) ; écarts expliqués.
- **Luna** (`tools/banc_parties.py --fil`, 2 passes en parallèle, `main` 8855312 puis la branche) : bancs
  `signes-ecart`, `signes-noir`, `signes-guet` ; « observer Ilse » dans le noir 0 appel ; les réponses ne disent
  que les signes reçus et leurs impressions, avec leur incertitude ; aucune attitude prêtée, aucune fuite du
  guet caché, aucune impression répétée à l'identique.
- Docs : `docs/plan-relations.md` (§ 6 : réglages retenus et pourquoi, relecture, limites), `docs/etat-dev.md`
  (« Branche `codex-signes-calibration`, non fusionnée », compte de tests ; « À revoir » : ce qui est réglé,
  ce qui reste). Pour le contexte des lots suivants, `docs/plan-agendas.md` (3e et 3f y deviennent A2 et A3),
  sans élargir ce lot.

## Livraison
Commits signés ; pousse la branche sur `origin` (pas `main`). Rapport dans
`docs/taches/rapport-codex-21-signes-calibration.md` : chaque invariant, fonctions, clés des caches, grille
mesurée (tableau complet), réglage retenu, coûts avant → après, Luna, constat des vols vus, limites.
