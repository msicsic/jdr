# Tâche Codex 223 : un secours se réévalue et s'acquitte sur ce qui a été constaté

Issu du diagnostic 222 (`docs/taches/rapport-codex-222-anselme-coups.md`, « Coups historiques » et « Attribution »). Crue 2024
(base `4d4c625`), 672–673 min : Gorm frappe Brune pour protéger Aubin ; Brune, aussi sa protégée, crie ; après la fuite de Gorm,
`defense.protection` retient ce **même cri non examiné**, `planification.reagir` (aide sans ennemi) le renvoie vers Brune, qui
redevient son danger à l'arrivée : il refuit. **Cinq allers-retours** ; seule l'étape `inspecter` acquitte le cri
(`pnj._executer`), étape jamais atteinte dans ce cycle. Les captures 022 et 026 du lot 222 montrent la même décision sur la base
et sur l'intégration actuelle. Le contrat d'engagement (lot 213, en cours) ne suffit pas : la défense précède `_candidats`.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Un autre lot calcule sur ce poste (213) : au plus 2 processus, priorité réduite.
Fichiers : `defense.py` (`protection`), `planification.py` (**seulement** `reagir`), l'acquittement du secours dans `pnj.py`
(**seulement** l'étape `inspecter`/`_executer` concernée ; le lot 206 b modifie les témoins et la perception, le lot 213
l'admissibilité de l'étape en tête : n'y touche pas), et leurs tests ; **pas** `deliberation.py` (lot 213), `social.py`,
`esprits.py`, ni le MJ. **Bruts dans `C:\Users\msics\donjon\artifacts\secours-223\`** ; captures du lot 222 dans
`C:\Users\msics\donjon\artifacts\anselme-coups-222\`. Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 222, 155 (fuite et lumière, auteurs actifs), 167 c (protéger, secours aux liens), 53 (peur
transmise), puis `defense.protection`, `planification.reagir` et l'acquittement d'un secours.

## L'invariant
**Un secours (cri, appel à l'aide d'un protégé) se réévalue sur ce que le protecteur a constaté depuis : s'il a vu la scène, le
danger connu et l'état du protégé décident (aider, fuir, rester) et le cri est acquitté par ce constat, même sans étape
`inspecter` ; un cri ancien ne recrée pas un aller-retour vers un lieu où le protecteur sait qu'un danger l'attend.** Les
préemptions légitimes et les vrais secours restent permis ; même règle pour tout protecteur, joueur compris s'il entend un appel ;
aucune règle propre à Gorm, Brune ou au scénario.

## Vérification
- Reproduire d'abord le cas avec les captures 022/026 du lot 222 sur l'intégration actuelle.
- Tests après rechargement : Gorm ne refait plus l'aller-retour ; un secours réel reste suivi jusqu'à constat ; un autre cas de
  même nature (autre protecteur, autre scénario) ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, cinq scénarios (dont `crue_hameau`) et `rixe` × quatre graines, références du cache, **avec le compteur 219**
  (classes) : répétitions suspectes, secours, coups ; aucune usurpation, plantage ni boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-secours-acquitte` poussée (pas `main`) ; si la poussée
est bloquée, laisse le commit local et dis-le. `docs/etat-dev.md` (« Branche `codex-secours-acquitte`, non fusionnée ») ; rapport
d'une page `docs/taches/rapport-codex-223-secours-acquitte.md`.
