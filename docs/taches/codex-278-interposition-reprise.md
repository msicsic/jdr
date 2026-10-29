# Tâche Codex 278 : une interposition reprise revalide ses deux cibles

La vérification d'intégration 274 (`docs/taches/rapport-codex-274-verif-integ.md`, fusionné ; archive
`C:\Users\msics\donjon\artifacts\verif-integ-0bad227\crue-hameau-12h\crue_hameau_1985.json.gz`) relève au hameau 1985 (`crue_hameau`, départ tiré, joueur passif `chambre_cloche`) :
Gorm (`marchand`) reprend à `385475` (642 min) le but « interposer Brune contre Aubin dans l'antichambre », 7,38 min
après sa suspension à 635 ; il s'était interposé à 636, puis avait changé de cible vers Ilse au relevé 640 ; Aubin quitte
l'antichambre à 642 (conduite basse puis refuge) **avant** la réactivation du but. Le compteur 219 le classe suspect.
L'agent conclut : il faut établir si le but repris est admis ou refusé quand la menace a quitté le lieu.

## L'invariant
**Une interposition reprise après interruption revalide, d'après les croyances actuelles du protecteur, la présence et
la position de ses deux cibles (le protégé et la personne crue menaçante) avant d'être choisie et à chaque étape
exécutée ; si la menace n'est plus crue dans le lieu ou à portée du protégé, le but cesse (fin attestée) au lieu de
reprendre.** Même juge au choix, à la replanification et à l'exécution (`pnj.refus_etape` et son raccord commun).
Aucun délai, aucune lecture de position réelle, aucune exception de personnage, de lieu ou de scénario.

**Commence par établir** sur une capture de la nuit (juste avant 635, puis avant 642) ce que Gorm croit d'Aubin à 642
(lieu, source, date) et quel chemin du code reprend le but : choix, `_reprendre_*`, agenda `garder`/`protéger`, ou
interposition du lot 167. Si Gorm croit encore Aubin dans l'antichambre faute de l'avoir vu partir, la reprise est juste
selon ses croyances : rapporte-le (`QUESTION : …`) au lieu de corriger.

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance). **Poste : le PC fixe**, deux
processus au plus, priorité réduite (une suite complète y tourne : un seul processus tant qu'elle n'est pas finie).

**Fichiers attendus** : `donjon/deliberation.py`, `donjon/pnj.py` (raccords), `donjon/planification.py` seulement si le
juge commun s'y trouve. Le lot 277, non fusionné, modifie `planification.py` et `echanges.py` : raccords minimaux, dis
dans le rapport chaque fonction touchée. Ne touche pas `agendas.py`, `signes.py`.

## Vérification
- Capture réelle rechargée (hameau 1985, avant 642) : Gorm ne reprend pas l'interposition contre une menace partie ; la
  même scène avec Aubin resté dans l'antichambre la reprend. Autre cas de même nature (autre scénario ou autre
  protecteur, présence changeante). Monde, rendu et scène identiques après recharge et laps entier/découpé.
- Tous les fichiers de tests qui exercent les fonctions modifiées (trouve-les par recherche des appelants).
- Banc rapide 4 h, cinq scénarios × quatre graines, référence de l'intégration à ta base (cache si présent, sinon
  calculée une fois), sonde actuelle (lots 265, 271, 276) : suspects 219 par nuit sans hausse, coups, S/F/D (fonction
  `cats` du lot 183). Calcul long détaché.

## Livraison
- Branche `codex-interposition-reprise` poussée ; si la poussée échoue depuis le PC fixe, laisse le commit local et donne
  son hash, sans passer par l'API GitHub. Rapport d'une page `docs/taches/rapport-codex-278-interposition-reprise.md` ;
  entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans `C:\Users\msics\donjon\artifacts\interposition-278\`.
  Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
