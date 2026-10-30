# Tâche Codex 360 : les régressions de la fin de garde apprise par ouï-dire (lot 337)

La suite complète de l'intégration `f014c80` (après le lot 356) donne 101 échecs et 3 erreurs (71 méthodes). Le lot 356
a attribué chacune à la fusion qui l'a fait basculer (annexe `docs/taches/attribution-codex-356-suite-rouge.md`). **23
méthodes, classées « régression réelle », basculent à la fusion du lot 337** (`c9b972b7`, `codex-fin-garde-ouidire`,
A4b : fin de garde apprise par ouï-dire) et restent rouges : liste exacte dans
`C:\Users\msics\donjon\artifacts\suite-f014c80\regressions-337.txt` ; suite brute dans `suite-f014c80\suite.log`
(copie sur le laptop) et `C:\Users\msics\donjon\artifacts\suite-f014c80-f014c80\` sur le PC fixe. Un défaut du 337
(`porteur=None` dans le rendu social) a déjà été corrigé pendant la reprise du lot 315 : il n'explique pas ces 23.

Lis `AGENTS.md`, `docs/etat-dev.md` (court), le rapport 337 et le rapport 356 avec son annexe. Pour un lot ancien, cherche
dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant (un seul)
Retrouver le contrat commun que le 337 a changé sans le vouloir. Le 337 voulait qu'un gardien apprenne la fin de sa garde
par une parole entendue (ouï-dire) ; ces 23 tests portent sur d'autres parcours (parole, ouïe, témoins, besoins,
délibération, appels…). **Corrige l'invariant commun touché, sans cas particulier, en gardant ce que le 337 garantit**
(ses propres tests verts). Si un test s'avère une attente devenue fausse par un changement voulu et documenté du 337,
prouve-le (citation du rapport, scène, avant/après) et adapte seulement ses prémisses, jamais ses assertions de sécurité ;
sinon c'est le code qu'on corrige.

## Vérification
Les 23 méthodes, les tests du 337 et les fichiers voisins verts sur l'intégration actuelle. Empreintes 2 h, quatre
graines, Relais, mine, auberge, crue, hameau (`tools/comparer_bancs.py --reference main`, cache) si le code change. Pas
de suite complète (le superviseur la relance), ni Luna.

## Contraintes
**Poste : le PC fixe.** Deux processus au plus, priorité réduite, calculs longs détachés. Le lot 361 (laptop) adapte des
tests périmés (G5, G16, U-C) : ne touche pas à ces fichiers de tests-là ; signale tout recouvrement.

## Livraison
- Branche `codex-regressions-337`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de
  l'utilisateur ; poussée autorisée).
- Rapport d'une page `docs/taches/rapport-codex-360-regressions-337.md` ; entrée « non fusionnée » de 8 lignes au plus
  dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\regressions-337-360\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
