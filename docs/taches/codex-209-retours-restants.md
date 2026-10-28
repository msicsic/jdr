# Tâche Codex 209 (diagnostic) : quels retours de décision restent après 200, 201 et 204, et à quel lot reviennent-ils ?

Suite du diagnostic 196 (`docs/taches/rapport-codex-196-changements-avis.md`) et du compteur 199 : la parade générale aux
changements d'avis intempestifs (demande de l'utilisateur du 2026-10-27) avance par lots (201 = 196 a fusionné ; 205 = 196 b
en cours : évacuation et traversée de l'eau ; 196 c à venir : contrat d'engagement dans `choisir`, intentions à `plan == []`).
Sur l'intégration actuelle (lots 200, 201 et 204 fusionnés), un banc de 4 h, cinq scénarios × quatre graines, compte encore
**57 retours non justifiés** : hameau 24, crue 27, auberge 5, mine 1, Relais 0 (bruts `C:\Users\msics\donjon\artifacts\essai-204\`
sur le laptop ; rejoue ici). Le lot 208 a aussi relevé, en crue 2024 tirée, Ilse qui alterne aide → aucune intention → aide
(`_secours_crus` perd puis retrouve Brune dans sa perception) et Aubin abri → aucune intention → abri.
**Diagnostic seul : aucun fichier du jeu modifié**, pour cadrer exactement le lot 196 c et ce qui resterait après lui.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (205, 195) : **un seul processus**,
priorité réduite. **Bruts dans `C:\Users\msics\donjon\artifacts\retours-209\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne)
ou `QUESTION : …`.

Lis `AGENTS.md`, les rapports 196, 199, 201, 204 et 208, puis le brief 205 (`docs/taches/codex-205-evacuation-juge-unique.md`)
pour savoir ce qu'il couvre.

## Ce qu'on te demande
1. **Inventaire** des retours non justifiés de l'intégration actuelle (même banc : cinq scénarios dont `crue_hameau`, graines
   1985/7/42/2024, 4 h, `tools/comparer_bancs.py` ou `tools/audit_nuits.py` avec le compteur) : pour chacun, PNJ, minute, les deux
   décisions, la cause dans le code (fonction, condition) et la famille (eau/évacuation, engagement à `plan == []`, candidat qui
   disparaît et revient avec la perception, garde/ronde, autre).
2. **Attribution** : ce que le lot 205 doit couvrir d'après son brief, ce que le lot 196 c couvrira d'après le § 4 du rapport 196,
   ce qui ne relève d'aucun des deux. Pour les cas Ilse 33/34 et Aubin 82 du lot 208 : disent-ils un défaut du contrat
   d'engagement (196 c) ou de la perception d'un protégé (une croyance perdue alors que rien n'a changé) ?
3. **Proposition** : pour ce qui reste hors 205 et 196 c, l'invariant général à rétablir et un petit lot par invariant ; une
   capture rechargeable par famille.

## Livraison
Branche `codex-retours-restants` (depuis `integration`) : `docs/taches/rapport-codex-209-retours-restants.md` (deux pages au plus,
un tableau famille → cas → cause → lot) et une ligne dans `docs/etat-dev.md`. Commit et poussée ; si la poussée est bloquée,
laisse le commit local et dis-le.
