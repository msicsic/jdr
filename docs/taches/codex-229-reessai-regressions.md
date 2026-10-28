# Tâche Codex 229 : les deux tests changés par le lot 225 (réessai lié à l'obstacle)

La suite complète de l'intégration `881db69` (lots 221, 224, 225) a quatre échecs hors MiMo. La bissection
(`C:\Users\msics\donjon\artifacts\integ-225\suite.log`, commits de fusion rejoués un par un) attribue au **lot 225** :
- `tests.test_dynamique_besoins.TenirTests.test_lucien_rapporte_la_lanterne_de_l_etable_au_grenier_au_lieu_d_aller_et_venir`
  (`len(set(lieux[-5:])) == 1` : 3 ≠ 1) ;
- `tests.test_lampes_parts.PartsPourSourcesTests.test_cas_reel_auberge_apres_huit_heures_l_huile_achetee_recharge_la_lanterne_vide`
  (Odile « refuse de se séparer du pot d'huile à lampe, qui lui sert », cause `necessaire`, au lieu de vendre une part).

Les deux passent sur `346c1aa` (avant 225) et échouent sur `881db69` et après.

Premier relevé de l'orchestrateur sur l'intégration actuelle (à confirmer) :
- Lucien renonce au coffre d'Anselme « trop sombre, là », puis obtient le bougeoir de Mireille.
- Il va au grenier vers 140 min.
- Puis, le noir étant levé, il retourne 65 min à la chambre au poêle et repart au couloir vers 235 min.

Ce peut être l'invariant de 225 qui joue juste (obstacle changé, reprise permise) ou une alternance garde/vol.
Pour l'huile, la nuit de 8 h a changé.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus, priorité réduite.

**Fichiers** : les fonctions de renoncement et de reprise du lot 225 (`deliberation.py`, `esprits.py`, raccords
`pnj.py` déjà ouverts par 225) et ces deux fichiers de tests. **Pas** :
- `planification.py` (lot 218) ;
- `biens.py`, `echanges.py`, `pnj_propositions.py` (lot 228) ;
- `ouie.py` (lot 195) ;
- `appel.py`, `deliberation._attendre_qui_vient`, `attendre_l_appelant` (lot 230) ;
- le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\reessai-229\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Lis `AGENTS.md`, le rapport 225 et la décision du 2026-10-27 (3 B) dans `docs/etat-dev.md` : patience de 30 min
gardée ; le répit de 60 min est remplacé par la cause du renoncement, jamais par le seul délai.

## Ce qu'on te demande
1. Pour chaque test, la première divergence entre `346c1aa` et l'intégration : minute, PNJ, décision, cause retenue.
   Puis le verdict :
   - **comportement juste** selon l'invariant de 225 (obstacle cru levé ou moyen nouveau) ;
   - ou **défaut** (reprise sans cause changée, cause mal retenue, alternance sans entrée nouvelle).
2. Défaut : corrige l'invariant commun, sans cas propre à Lucien, Odile, une lanterne ou l'auberge. Tests après
   rechargement, cas réel et un autre de même nature, même laps d'un bloc ou découpé.
3. Comportement juste : adapte le test à son intention, avec la preuve dans le rapport. Les intentions sont :
   - pas d'aller-retour sans entrée nouvelle ;
   - la lumière ramenée à la garde ;
   - l'huile vendue quand elle n'est pas nécessaire au vendeur.

   **Aucune assertion affaiblie sans cette preuve**, aucune capture réancrée sans la dire.

## Vérification
- Les deux tests et les tests ciblés du lot 225 verts.
- Si du code moteur change : banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219
  (suspects, à expliquer).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-reessai-regressions` poussée (pas `main`). Si la poussée est bloquée par la revue, laisse le commit
  local et dis-le.
- `docs/etat-dev.md` : « Branche `codex-reessai-regressions`, non fusionnée ».
- Rapport d'une page `docs/taches/rapport-codex-229-reessai-regressions.md`.
