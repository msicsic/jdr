# Lot 439 — les coups du hameau 2024

31 octobre 2026, PC fixe, `codex-coups-hameau`, départ `693200b4`, base intégration
`60f857c5`. **Diagnostic seul : 35 coups conformes aux croyances enregistrées
et aux règles existantes ; aucune régression de décision établie.** Code inchangé.

**Reproduction.** `4539dd68` détaché, `crue_hameau`, graine 2024, départ tiré,
12 h, joueur passif en `chambre_cloche` : **35 frappes, 18 touchées**, chronique
et empreintes identiques à l'archive 402. Une seule rixe, à 674 min,
`t=404500–404726` (22,6 s). Un processus détaché à priorité réduite, 1 019 s.

Épisodes imbriqués ; coûts recalculés à froid avant **chaque** coup, en minutes
de plan ; « prix » = `combat.prix_violence`, compris dans le coût total.
La défense passe avant les paliers ; `contrat_intention` peut décrire le but interrompu.

| Auteur → cible ; instants | Frappes/touchées | Cause et verdict | Prix ; coût / recours pacifique | Preuve |
|---|---:|---|---|---|
| Aubin → Maël ; 404500–404535 | 2/0 | Manger `vivres_3`, faim, palier 3 désespoir : conforme | 28,54 → 28,52 ; 40,51 → 40,48 / aucun plan | `coups.json` 1–2 ; `recours.json` |
| Ilse → Aubin ; 404556–404726 | 11/6 | Violence d'Aubin perçue contre Maël ; riposter : conforme | 0 ; 4,23 → 3,14 / aucune fuite admise | `controle-coups-4539.json`, danger Aubin |
| Brune → Aubin ; 404595–404725 | 7/6 | Même danger perçu ; riposter : conforme | 3 ; 6,67 → 5,62 / fuite 6,72 → 7,72 | Même contrôle, comparaison avant les sept coups |
| Gorm → Aubin ; 404600–404690 | 6/4 | Même danger perçu ; riposter : conforme | 0 ; 3,40 → 2,36 / fuite 9,22 → 11,96 | Même contrôle ; douceur 100 autorisée en défense |
| Aubin → Gorm ; 404600–404720 | 9/2 | Coup reçu de Gorm, dangers Gorm/Brune/Ilse ; riposter : conforme | 4 ; 7,67 → 8,23 / aucune fuite admise | Même contrôle, danger Gorm et cible consciente |

**L'embuscade.** Adoptée à 658 min : faim **95,796**, prix **36,18**,
coût **49,92**. Premier coup : faim **97,387**, douceur 80, courage 50,
prix **28,54 ≤ ENJEU 60**. Le seuil corporel 95 permet d'assumer les témoins :
Gorm, Brune et Sève crus à vue, Ilse aussi à portée d'ouïe. Les deux coups
manquent. Sans violence : graphe épuisé (**un nœud**, aucune borne atteinte)
à l'adoption et avant les deux coups ; aucun marché via `plan_recours`.

**Recours exclus.** Les trois lots portés par Aubin sont crus consommés.
`vivres_1` est cru indisponible ; `vivres_3/5` restent crus chez Maël. Demandes
refusées `necessaire` à 445, toujours retenues ; achat bloqué, avec seulement
**une pièce pour un prix de deux**. Troc de la torche refusé `garde`
à 445, puis `epuise` à 658. Ilse, Brune et Sève ont répondu `rien` aux enquêtes
de faim (404/429/494) ; aucune aide attendue. Réserve crue verrouillée, sans
clé, crochetage ni outil pour la forcer. Pour Ilse et Aubin, la porte haute
reste crue verrouillée ; les routes basses sont refusées pour péril d'eau.
Gorm et Brune peuvent fuir, mais plus cher à chaque coup.

**Arrêt et recharge.** Toutes les cibles sont conscientes et au contact lors
des 35 validations ; les 33 ripostes visent un danger enregistré. Aubin tombe
à 0 PV à `404726` : aucun coup ensuite ; Gorm le ranime à `405600`, à 1 PV.
Un seul inconscient ici, aucun assomment réussi ; « deux assommés » au 402
concerne toute sa campagne. **77 captures** (avant/après chaque
coup, six choix violents, fin) : état, `regarder` et `scene_percue` identiques
après sauvegarde/recharge, sans mutation par le contrôle. Corvus, éloigné,
n'assiste pas directement aux coups.

**Portée causale.** `0bad227` rend les mêmes plans, prix et coûts sur les
35 photographies, y compris sans violence (`controle-coups-0bad.json`).
Comparaison de décisions, pas rejeu ancien : validation de son schéma
désactivée pour accepter les métadonnées récentes. Son archive, non relancée,
suit une autre trajectoire (service accepté à 82, absent actuellement).
Aucun lot fautif identifié : ni bissection ni correctif proposé. Divergence
des nuits non attribuée ; les autres arbitrages sociaux ne sont pas certifiés.

La nourriture visée est réellement épuisée, mais sa disponibilité n'est pas
connue d'Aubin : cause interne `epuise`, parole « refuse l'échange »
(`pnj_propositions.executer`). Choix admissible ne garantit pas sa réussite.
Ni Luna, suite complète ni calcul actif. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/coups-hameau-439/`
(`FIN-rejeu.json`, `bilan.json`, `moyens.json`, `recharges.json`).
