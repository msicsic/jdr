# Tâche Codex 219 : le compteur des changements d'avis distingue répétition, préemption légitime, progression et satisfaction

Recommandation 4 de la revue 217 (`docs/taches/rapport-codex-217-revue-vierge-decisions.md`) et avertissement du diagnostic 209
(« 57 retours ≠ 57 défauts ») : le compteur du lot 199 (`tools/detecter_changements_avis.py`, intégré à `tools/audit_nuits.py` et
`tools/comparer_bancs.py`) signale un retour `D1 → D2 → D1` sans entrée nouvelle, mais il compte ensemble de vraies boucles et des
cas légitimes : une ronde préemptée par un secours (palier supérieur), un but repris après un progrès réel, un besoin satisfait par
autrui pendant l'interruption. Il ignore aussi les dérives ouvertes `A → B → C` sans retour, et ne dit pas si un service payé a
réellement donné l'état attendu (revue 217 : Brune éteint la torche payée une minute après). Les lots qui corrigent les décisions
(213 en cours, 218 en attente) en ont besoin pour juger leurs mesures. **Outils seulement : aucun fichier de `donjon/` modifié.**

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille) :
au plus 2 processus, priorité réduite. Fichiers : `tools/detecter_changements_avis.py`, `tools/audit_nuits.py`,
`tools/comparer_bancs.py` (affichage), et leurs tests. **Bruts dans `C:\Users\msics\donjon\artifacts\transitions-219\`.** Termine
par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 196 (§ 3, limites du détecteur), 199, 209, 217, puis le détecteur et ses tests.

## L'invariant
**Chaque retour de décision relevé est classé par une seule règle, d'après les données de la nuit : préemption par un palier
strictement supérieur ; progression réelle entre le départ et le retour ; satisfaction ou démenti par autrui ; répétition sans
entrée nouvelle (seule classe qui compte comme suspecte) ; et à part, les dérives ouvertes et les services payés dont l'état
attendu n'a pas duré jusqu'à la fin convenue.** La classification lit les mêmes sondes, sans modifier la nuit (identité avec et
sans sonde conservée) ; aucune règle propre à un personnage, un but ou un scénario.

## Vérification
- Rejouer les 57 cas du diagnostic 209 (inventaire dans `C:\Users\msics\donjon\artifacts\retours-209\` : copie depuis le PC fixe
  par `scp msics@msi-desktop:C:/Users/msics/donjon/artifacts/retours-209/...` si absent) et montrer la classe de chacun ; les 21
  secours et rondes doivent séparer préemptions légitimes et vraies répétitions.
- Tests courts sur des épisodes synthétiques de chaque classe et sur le cas de la torche de Brune (hameau 1985, minutes 7–8).
- Banc rapide 4 h, cinq scénarios × quatre graines, sur l'intégration actuelle : tableau par classe ; identité des nuits avec et
  sans sonde (états complets, chroniques, mesures).
- Tests des outils modifiés verts ; pas de suite complète du jeu nécessaire (aucun fichier de `donjon/` modifié).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-audit-transitions` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-audit-transitions`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-219-audit-transitions.md`.
