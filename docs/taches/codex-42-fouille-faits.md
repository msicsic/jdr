# Tâche Codex 42 : une fouille ne s'établit pas comme un fait narratif

Branche `codex-fouille-faits` (elle porte ce fichier, issue de l'intégration **de74ec1** : lots 38 à 40 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant,
vérification minimale, rapport d'une page. **Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt
principal ; copies seulement).

Un autre lot tourne sur l'autre poste (41, routes et eau : `planification.py`, `trajet_estime.py`, `pnj.py`,
`eau.py`). Ne touche pas à ces fichiers.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-perception-geste` lot 34, `codex-absence-vue` lot 40,
`codex-luna-restes`), `docs/contrat-mj.md` (trois niveaux ; perception active ; faits narratifs), puis
`donjon/faits_locaux.py` (`preparer_faits`, le rendu « Tu remarques … » vers la ligne 521), `donjon/mj.py`
(choix entre `etablir_faits` et une action de perception, contre-revue), `donjon/narration.py`
(`INSTRUCTIONS_AUDIT` : indices), `donjon/consignes.py` (ce que le MJ sait d'`etablir_faits` et d'`examiner`).
Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-8443458\relecture.txt` (relais n° 5, les quatre parties).

## Le constat (vérification Luna d'intégration 8443458, deux passes)
« je cherche des traces de pas sur le sol » (banc `relais`, saisie n° 5) : sur `main` et en 3b6415b, Luna proposait
`examiner` (trois parties sur quatre) ; sur l'intégration, dans les deux passes, elle passe par `etablir_faits`, et
le joueur lit « Tu remarques un sol sur le sol. » puis « Tu remarques une surface du sol sur le sol. La poussière
forme par endroits une fine pellicule irrégulière sur la pierre, où des traces de pas pourraient se distinguer. »
Ce dernier aspect, enregistré, ressemble à un indice. La cause du basculement n'est pas établie (le prompt
d'interprétation n'a pas changé depuis 3b6415b ; le contexte reçu, oui).

## L'invariant
**Ce que révèle une recherche, une fouille ou un examen est le résultat d'une perception exécutée par le moteur,
jamais un fait établi par le MJ.** Un ajout d'`etablir_faits` qui répond à une demande de perception active, ou qui
pose un indice (traces, marques, signes d'un passage, ce qui serait caché), est refusé avec un `attendu` qui dit
d'employer la perception (`examiner`, `fouiller`…) ; la perception du moteur donne son résultat, positif ou négatif.
`etablir_faits` reste légitime pour un détail d'ambiance ou matériel sans valeur d'indice ; s'il est rendu, un détail
ancré sur un support ne le répète pas (« Tu remarques un sol sur le sol » est impossible quel que soit le nom).
Trouve d'abord pourquoi Luna a basculé (fil complet de la partie, contexte reçu) et corrige la règle commune (refus
du moteur, consignes au MJ là où une règle manque vraiment, rendu), pas la saisie « traces de pas ».

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (fouille du sol au Relais), un autre de
  même nature (chercher une marque sur une porte ou fouiller un coin ailleurs) : `etablir_faits` refusé avec
  `attendu`, perception exécutée, résultat du moteur affiché et sauvegardé ; un détail d'ambiance légitime accepté
  et rendu sans doublon de son support.
- Luna, **une passe** : `relais`, `crypte`, `atelier`, `luna-restes-ambiance`, `tools/banc_multi.py` avec la
  référence `main` lue du cache (voir le rapport du lot 40 pour lancer la référence avec son outil historique) ;
  appels par tour, texte affiché pour relais n° 5.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` (fouille et faits narratifs), `docs/etat-dev.md`
(« Branche `codex-fouille-faits`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-42-fouille-faits.md` (cause du basculement, invariant, fonctions, mesures, limites).
