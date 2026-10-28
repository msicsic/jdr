# Tâche Codex 227 : le compteur distingue un service défait par son auteur d'un état qui cesse seul

Le compteur des retours de décision (lot 219, `tools/detecter_changements_avis.py`) relève à part les « états payés perdus après
réussite ». Depuis la décision de l'utilisateur du 2026-10-27 (lot 224, fusionné) : **celui qui a été payé ne défait pas lui-même
l'état obtenu tant qu'il croit le bénéficiaire présent ; il n'a aucune obligation d'entretien** (un feu qui s'éteint faute de
combustible n'est pas sa faute). Le rapport 224 montre que le compteur brut reste à **6 → 6** : quatre extinctions précoces du
Relais sont évitées, mais le compteur relève ensuite l'**épuisement naturel du combustible**, que la règle ne demande pas
d'empêcher ; deux extinctions au hameau restent permises parce que le prestataire croit le bénéficiaire ailleurs. Le compteur
mesure donc mal ce que la règle exige. **Outils seulement : aucun fichier de `donjon/` modifié.**

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots calculent sur ce poste (195, 226) : **un seul processus**,
priorité réduite. Fichiers : `tools/detecter_changements_avis.py`, `tools/audit_nuits.py`, `tools/comparer_bancs.py` (affichage)
et leurs tests. **Bruts dans `C:\Users\msics\donjon\artifacts\compteur-227\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

Lis `AGENTS.md`, les rapports 219 et 224, puis la classe « état payé perdu » du détecteur et ses tests.

## L'invariant
**La perte d'un état payé est classée selon sa cause, d'après les données de la nuit : défaite par le prestataire alors qu'il
croyait le bénéficiaire présent (seule classe fautive), défaite par le prestataire quand il le croyait parti (permise), défaite par
le bénéficiaire ou un tiers, ou cessation d'elle-même (combustible épuisé, cause physique).** La classification lit les mêmes
sondes et ne modifie pas la nuit (identité avec et sans sonde) ; aucune règle propre à un personnage, un état ou un scénario.

## Vérification
- Rejouer les six cas du banc 224 (bruts du lot 224 dans `C:\Users\msics\donjon\artifacts\service-224\` sur ce poste) et le cas de
  la torche de Brune (revue 217) : classe de chacun, avant et après la règle du lot 224.
- Tests courts de chaque classe.
- Banc rapide 4 h, cinq scénarios × quatre graines sur l'intégration actuelle (`881db69`) : tableau par classe ; identité des
  nuits avec et sans sonde.
- Tests des outils modifiés verts ; pas de suite complète du jeu nécessaire.

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-compteur-services` poussée (pas `main`) ; si la poussée
est bloquée, laisse le commit local et dis-le. `docs/etat-dev.md` (« Branche `codex-compteur-services`, non fusionnée ») ; rapport
d'une page `docs/taches/rapport-codex-227-compteur-services.md`.
