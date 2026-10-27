# Tâche Codex 218 : un plan qui suspend une garde la restaure jusqu'au bout

Issu du diagnostic 209 (`docs/taches/rapport-codex-209-retours-restants.md`, famille « Précondition temporaire », n° 38, et
« Deux lots supplémentaires » : **restauration des charges**). Cas réel : hameau 1985, Gorm, minute 6 : il doit livrer
`vivres_6` à Aubin (parole donnée) ; il déverrouille la réserve, puis abandonne la livraison pour **reverrouiller** la réserve,
puis reprend la livraison en la déverrouillant de nouveau. Cause relevée : la branche `remettre` de `planification._pulsion` passe
par `_devis_remise` et livre un plan **sans la restauration du verrou** ; `deliberation.retabli_par_son_plan` exige une étape
`verrouiller`, absente ; la garde des biens (palier 4) passe alors devant la parole due (palier 5) et défait le progrès du plan. Le
lot 103 (garde-manger) et le lot 201 (196 a) ont traité des cas voisins sans ce chemin. Capture rechargeable :
`C:\Users\msics\donjon\artifacts\retours-209\` (`crue_hameau-1985/avant-0.json`, abandon à t=3600), copiée sur le laptop si besoin
depuis le PC fixe (`scp msics@msi-desktop:...`).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille) :
au plus 2 processus, priorité réduite. Fichiers : `planification.py` (`_pulsion`, `_devis_remise` et le devis/plan publié qui
porte la restauration), `deliberation.py` **seulement `retabli_par_son_plan`** (le lot 213 modifie `choisir`, `_candidats`,
`_continuer_progres`, `secours` : n'y touche pas), et leurs tests ; **pas** `social.py`, `esprits.py`, `pnj.py` (lot 206), ni le MJ.
**Bruts dans `C:\Users\msics\donjon\artifacts\charges-218\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 209, 103 (garde-manger, remise sous clé prévue), 201 (`retabli_par_son_plan` sans
auto-exclusion), 196 § 4.2, puis `_pulsion`, `_devis_remise`, la découpe des plans de livraison et `retabli_par_son_plan`.

## L'invariant
**Un plan qui suspend une charge de son auteur pour agir (déverrouiller sa réserve, ouvrir sa porte, laisser son poste) porte cette
suspension et sa restauration jusqu'à son terme, aussi après une découpe pour livraison ou une replanification ; tant que ce plan
est en cours, la garde de la charge suspendue ne le combat pas. La garde reprend si le plan est abandonné ou fini sans restaurer.**
Même règle pour tout PNJ, tout contenant, porte ou poste, et pour toute tâche (parole, service, vente) ; aucune règle propre à
Gorm, à la réserve ou au scénario ; pas d'ajout isolé d'une étape `verrouiller` présenté comme garantie générale.

## Vérification
- Reproduire d'abord le cas réel sur la base (capture), dire ce que la base fait et pourquoi.
- Tests après rechargement : Gorm livre sans reverrouiller entre-temps et la réserve est restaurée après ; un autre cas de même
  nature (autre contenant ou porte, autre PNJ, autre scénario) ; plan abandonné : la garde reprend ; même laps d'un bloc ou
  découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) × quatre graines, références du cache, **avec le compteur 199** ; aucune
  usurpation, plantage ni boucle nouvelle ; coût (`tools/mesure_cout.py`, mine 4 h) sans hausse notable.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-restauration-charges` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-restauration-charges`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-218-restauration-charges.md`.
