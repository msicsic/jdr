# Tâche Codex 104 : « il y a quelqu'un ? » finit encore sur « Reformule-la » (N3 non clos)

Petit lot de correction (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** :
priorité réduite, au plus 2 processus de calcul, Luna en 4 exécutions au plus ; d'autres lots tournent (coût du planificateur,
boucle de garde-manger). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat
Le lot 100 (`codex-sans-message-technique`, fusionné) devait garantir qu'un tour ne finit jamais sur un message technique ni sur
l'abandon d'une intention valable ; sa passe Luna ne montrait plus N3. Mais la passe Luna du lot 102, sur une base qui **contient
le lot 100** (e218907), affiche de nouveau, à `soir-noir` saisie n°1 « il y a quelqu'un ? », **« Ta demande n'a pas été exécutée.
Reformule-la. »**, après trois appels (interprétation 5,7 s, revue de fidélité `auditer_action` 2,8 s, interprétation 3,8 s).
La saisie suivante, « « Qui est là ? » », est dite et la voix d'Ilse répond. Partie complète avec son fil :
`C:\Users\msics\donjon\artifacts\n3-soir-noir-lot102\20261026-022930-37884\lot-r1\…-soir-noir.json` (tour 1, champ `fil`).
Lis le rapport du lot 100 (`docs/taches/rapport-codex-100-sans-message-technique.md`) et ce que fait `mj.py` aujourd'hui.

## L'invariant (celui du lot 100, à fermer)
**Aucune voie ne produit « Ta demande n'a pas été exécutée. Reformule-la. » pour une saisie que le moteur sait traiter** : une
parole aux mots exacts du joueur est dite (comme le repli du lot 100) même quand la revue conteste le typage et que la
correction échoue. Trouve, dans le fil réel, la branche que le lot 100 n'a pas couverte (appels successifs, refus, champ en
cause) et ferme-la dans la chaîne commune ; puis cherche dans `mj.py` toutes les sorties qui peuvent encore produire ce message
et dis, pour chacune, pourquoi elle est légitime (saisie réellement inintelligible) ou la ferme.

## Vérification
- Rejeu exact du tour réel avec les réponses enregistrées de Luna (MJ simulé à partir du fil) : la parole est dite ; un autre cas
  de même nature (question à la cantonade dans une salle éclairée) ; état et rendu après rechargement.
- Garde de test : le message n'apparaît que pour une saisie inintelligible (cas explicite).
- Luna, une passe de `soir-noir` et `noms-dialogue` (deux exécutions) : N3 absent.
- Tests ciblés ; suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md` si utile, `docs/etat-dev.md` (« Branche `codex-n3-reformule`,
non fusionnée »). Rapport d'une demi-page : `docs/taches/rapport-codex-104-n3-reformule.md`.
