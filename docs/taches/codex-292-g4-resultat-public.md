# Tâche Codex 292 (refonte G4) : le résultat d'un geste se lit dans le rendu du moteur, sans récit ni audit

Deuxième lot de code de la refonte du MJ, après G2 (lot 291, fusionné). Lis `AGENTS.md` (« Contrat du MJ », clause de
transition), `docs/plan-refonte-mj.md` (ligne G4), `docs/conception-refonte-mj.md` (sections 2, 4 et 9, ligne G4) et
`docs/conception-valeur-llm.md` (section 7, ligne G4). La branche `origin/prompt-simplifie` est la base de réflexion :
son `jeu.py` affiche `rendre_resultat(resultat)` après exécution, sans récit.

## Le constat
Sur l'intégration, après `moteur.executer(plan)`, `conclure` (`jeu.py`, vers la ligne 255) calcule
`rendre_resultat(resultat)`, sauvegarde, puis appelle `raconter` → `MJ.raconter_resultat` : un récit de Luna du
résultat déjà appliqué, audité, avec repli sur le rendu du moteur. L'option `--recit-moteur` saute déjà ce récit. Coût :
un appel et son audit après chaque geste exécuté, alors que le moteur sait dire ce qui s'est passé ; risque : un récit
qui reformule un résultat mécanique (PV, inconscience, ligature, possession, lumière) et qu'il faut auditer.

## L'invariant
**Une exécution a un rendu complet après sauvegarde, sans reformulation : le joueur lit ce que le moteur a établi
(`rendre_resultat`), sans appel de récit à Luna ni audit après le geste.** « Complet » : chaque conséquence publique du
geste figure dans le rendu (jet et issue, blessure, état du corps, ligature/prise, possession et position d'un objet,
lumière, ouverture/verrou, paroles moteur que le geste produit), à partir des seules données perceptibles ou connues de
Corvus. Si une conséquence publique n'est pas rendue aujourd'hui, ajoute-la au rendu commun du moteur (une phrase sobre,
pas de littérature) plutôt qu'un cas propre à l'exemple.

Ce que le lot ne fait pas : pas de compilateur (G1), pas de clic (U-D), pas de rendu canonique des perceptions
(G5 : elles sont déjà rendues directement), des déplacements cumulés (G7) ni des paroles typées (G15 à G19), pas
d'ambiance (G8 à G11). La fiche tenter/annuler et les revues de la proposition avant exécution restent. Supprime
`raconter_resultat`, `raconter` et `--recit-moteur` seulement s'ils n'ont plus d'usage (Comparateur, outils, web) ;
dis ce qui reste.

## Fichiers attendus
`jeu.py` (`conclure`, `raconter`), `donjon/narration.py` (`rendre_resultat` et ce qu'il compose), sorties de
`donjon/moteur.py` seulement si une conséquence publique manque au résultat ; `donjon/mj.py` pour retirer ce qui n'a plus
d'appelant. Vérifie que la page web et la TUI passent par le même `conclure`. Ne touche pas aux mécaniques des PNJ.

## Vérification
- Tests ciblés, en console avec MJ simulé, la proposition validée puis « tenter » :
  - assommer (`force-4b-assommer`) et un autre coup (blessure sans inconscience) ;
  - ligoter (`force-4f-ligoter`) et une autre contrainte (prise ou traîner) ;
  - poser au sol (`poser-sol-relais`) et une autre possession (prendre, allumer).

  Pour chacun : texte affiché complet, zéro appel de récit ni d'audit après l'exécution, même effet du monde que sur la
  base, monde, fiche et carte identiques après recharge. Reprends les tests qui exercent `raconter_resultat`,
  `--recit-moteur` et le repli du récit ; trouve-les par recherche. Adapte seulement ceux dont l'attente était le récit
  de Luna, en le disant.
- **Luna, une passe**, scripts `force-4b-assommer`, `force-4f-ligoter`, `poser-sol-relais`, contre la référence de
  l'intégration (`tools/banc_multi.py --variante integ=<commit de ta base> --variante lot=.`, référence absente jouée une
  fois et rangée). Copies seulement, jamais `sauvegardes/`, `SEUIL_AUTH` vers le coffre du dépôt principal. Mesures :
  - appels et secondes par tour ;
  - zéro appel de récit ni d'audit après exécution ;
  - refus par cause, relances, replis ;
  - le texte de chaque résultat lu par le joueur, comparé à l'effet du monde.
- Lance la passe Luna détachée, avec un fichier de fin écrit même en cas d'échec (`ok`, codes, erreur), et vérifie
  qu'elle démarre (premier fichier de partie produit) avant de rendre la main. Le script d'analyse sépare un incident
  réseau de la référence du contrôle de l'invariant.
- Pas de suite complète (le superviseur la lance).

## Contraintes
**Poste : le laptop.** Une vérification d'intégration (lot 284) y tourne : deux processus au plus, priorité réduite ;
la passe Luna est légère.

## Livraison
- Branche `codex-g4-resultat-public` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) ;
  si la poussée échoue, laisse le commit local et donne son hash.
- Rapport d'une page `docs/taches/rapport-codex-292-g4-resultat-public.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\g4-292\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
