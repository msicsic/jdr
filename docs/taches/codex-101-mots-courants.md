# Tâche Codex 101 : un mot courant du français n'est pas du vocabulaire technique

Petit lot (`AGENTS.md`, « Rythme des lots »). **Luna disponible** pour une passe de contrôle, copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** :
priorité réduite, au plus 2 processus de calcul, Luna en 4 exécutions au plus ; d'autres lots tournent (coût du planificateur,
lot 100 sur les messages techniques dans `mj.py`/`narration.py` : ne touche pas à la chaîne de correction ni au repli). Termine
ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat (vérification Luna du lot 99, défaut N2)
`soir-appel`, passe 2, saisie n°5 : la réplique « les planches ne t'ont pas encore été données » est refusée pour le mot
« données », traité comme vocabulaire du jeu (méta-langage / voix d'auteur). Le refus, ajouté aux précédents, finit sur le repli
technique. Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-b0042c9\` (`constats.md`, `preuves-incidents.json`). Le lot 74
avait déjà retiré « refus » de ce garde comme nom commun ; d'autres mots du même garde peuvent avoir le même défaut.

## L'invariant
**Le garde lexical de méta-langage ne refuse un mot que dans son emploi technique**, jamais un mot courant du français dans son
sens ordinaire (participe « données », « faits » au sens d'actes, « moteur » d'un moulin…) : il juge l'emploi (terme de jeu
désignant le dossier, le moteur, le MJ, les identifiants, les champs) et non la seule forme. Revois **tout** le vocabulaire du
garde avec la même règle, pas seulement « données » ; pas de liste d'exceptions par exemple, une règle d'emploi commune.

## Vérification
- Tests après rechargement avec MJ simulé : la réplique réelle admise ; un autre mot courant du même garde admis dans son sens
  ordinaire ; un vrai méta-langage (« les données du jeu », « le moteur a refusé », un identifiant brut) toujours refusé avec son
  `attendu`.
- Luna, une passe de `soir-appel` et `ressources` : aucun refus de ce type, appels par tour.
- Tests ciblés ; suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` si le contrat du garde change, `docs/etat-dev.md` (« Branche
`codex-mots-courants`, non fusionnée »). Rapport d'une demi-page : `docs/taches/rapport-codex-101-mots-courants.md`.
