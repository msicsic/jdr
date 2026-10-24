# Lot 58 — une vue du niveau ne rajeunit pas une ancienne vitesse d'eau

24–25 octobre 2026. Branche `codex-eau-plan-marche`, **non fusionnée**, base
`c592d68` (fiche `6da6d06`). Aucun appel à Luna, aucun changement du MJ,
des scénarios, des seuils ou de `pnj_propositions.py`.

**Cause et contrat.** Les routes du lot 41 partagent leur admissibilité.
`eau.estimation` datait une ancienne vitesse avec la dernière vue du niveau
dans sa salle. À 368, Gorm alternait entre −8 et +8 cm/h, deux pentes mesurées
à 354 : recherche admise, marche refusée, puis constat effacé en revoyant
l'autre salle. La dernière vue ancre désormais le niveau ; le dernier repère
mesuré choisit la pente. Les égalités sont départagées par les valeurs,
indépendamment de la salle revue. Un premier repère ou un sol sec efface une
pente sans ses deux mesures.

Les repères sont déjà sauvegardés ; une mesure nouvelle peut établir la baisse.
`Vue`, la marche et `en_peril` partagent cette lecture ; `eau_route` et
`vitesse_eau`, déjà dans `_entrees`, couvrent son invalidation. L'eau inconnue
au seuil reste datée et sauvée par `observer(..., "essai")` : deux acteurs
vérifient que la recherche retire ensuite la route, après recharge.

**Captures et preuves.** Les archives `artifacts/verif-integ-5c2ce81/` sont
absentes. Rejeu ciblé dans un worktree détaché : captures versionnées de Gorm
2024 à 368 et d'Ilse 1985 à 247 (même boucle, avant les 258–264 de l'audit).
Sur vingt minutes depuis ces captures, ancienne lecture → corrigée : Gorm
**9 → 2 refus, 44 → 14 passages** ; Ilse **5 → 1 refus, 40 → 12 passages**.
Le premier refus peut viser le plan ancien inscrit dans la capture, les suivants
une mesure nouvelle. Monde complet et rendu identiques d'un bloc ou par
minutes rechargées ; la pente persiste quand on revoit une ancienne salle,
une baisse mesurée rouvre le passage. Les captures du lot 39 gagnent le sec, le détour de
`TrajetsRevelesTests` reste refusé.

**Validation finale.** Les 49 tests ciblés passent (dont les quatre nouveaux).
Audit branche seule, 12 h, sans plantage, usurpation ni écart d'état :

| Crue | Passages/h, pire | Eau (min·PNJ) | Sans recours | « eau longue » |
|---|---:|---:|---:|---:|
| 2024 | 20 | 220 | 245 | 0 |
| 1985 | 22 | 345 | 230 | 0 |
| 500 | 34 | 1 090 | 60 | 4 |

2024 : aucun refus de la marche sur l'eau ; 1985 : trois refus isolés à 190,
221 et 235. Restent des alternances de buts en début de nuit et douze
avertissements redits en 2024, hors de cet invariant.
Rapide final contre `c592d68` (cache de référence), 4 h × 1985/7/42/2024,
crue et Relais : aucun plantage, violation ni usurpation ; Relais inchangé.
Crue, maximum horaire moyen **24,75 → 17,75**, pire **46 → 30** ; eau
**83,75 → 87,5** min·PNJ ; sans recours **60 → 60**. Aucun temps du cache
comparé aux temps actuels. `VERIFIER` + `spatial.VERIFICATION=1`, 2 h,
crue 42/2024 : aucun plantage, écart ni borne (838/372 s).
Suite complète finale, une fois, `tools/tests.py --processus 3`, priorité
réduite : **1 800 tests, quatre ignorés, un échec**, 750,9 s. Cet échec social
est reproduit avec `eau.py` exact de `c592d68`
(seul fichier de code modifié) : `test_appel_negocie.QuoiTests.`
`test_cas_reel_mine_josse_dit_ce_qu_il_veut_gaspard_le_fait_venir` attend une
part promise ; Gaspard refuse puis accepte un échange. Aucun changement de
ce test ni de la négociation dans ce lot.

**Limites.** Observations en minutes, vitesse moyenne entre repères ; deux
mesures de même date peuvent différer. Découvertes et temps écoulé peuvent
invalider un départ. Ni fin générale des boucles ni baisse uniforme de l'eau
garanties. Bruts : `artifacts/codex-58/` du worktree.
