# Tâche : le coût de calcul d'une nuit, sans rien changer à ce que font les PNJ

Branche `cout-calcul`, worktree `.worktrees/cout-calcul`. Lis d'abord `AGENTS.md`, `docs/etat-dev.md`
(entrées `vitesse-banc`, `planif-rapide`, `perception-rapide`, `planif-cout`, `deliberation-evenements`,
`temps-reel`), `docs/plan-planificateur.md` (« Coût de calcul ») et `docs/plan-temps.md` (« Correctif :
délibérer à l'événement », point « Coût »).

## Le besoin
Les nuits ont ralenti à chaque chantier qui rendait les PNJ plus vifs (délibération à l'événement : mine
25 → 34 s, auberge 26,8 → 31,9 s ; le lot A temps réel un peu plus) ; chaque banc et chaque vérification
en paie le prix.

## Contrat
Rien ne change dans ce que décident les PNJ : chronique, mesures, récit, état final complet et empreintes
identiques à `main`, nuit par nuit, sur les quatre scénarios, départ tiré et fixe (au moins 4 graines
chacun, 8 h), avec `planification.VERIFIER` et `spatial.VERIFICATION` sur une nuit de chaque scénario.
`tools/comparer_bancs.py --empreintes` s'il est sur `main` (branche Codex `codex-outils`), sinon une
comparaison des sorties `banc_pnj --sortie` hors temps.

## Étapes
0. **Mesurer** : profil d'une nuit de 8 h de chaque scénario sur `main` (cProfile, au processeur) :
   part de la délibération (`choisir`, lectures de la vue), du planificateur (recherches neuves et
   reprises), de la perception, du corps au temps vécu, des trajets. **Essai PyPy** : le banc et la
   suite tournent-ils sous PyPy (Python 3.11 ; dépendances du banc seulement) ? Si oui, temps d'une nuit
   sous PyPy contre CPython, mêmes empreintes. Rapporte avant d'aller plus loin si PyPy change la donne.
1. **Reprendre le choix entier** : chaque choix entre deux minutes refait les lectures de `choisir`
   (vue du planificateur pour l'argent, l'abri, des chemins d'une étape) même quand rien de ce qu'il lit
   n'a changé ; la mémoire n'épargne que les recherches. Faire de tout ce que lit le choix une clé
   (comme `planification._entrees`) et reprendre le résultat quand elle n'a pas changé ; un mode de
   vérification (comme `VERIFIER`) refait chaque choix repris et compare, et signale toute lecture qui
   manque à la clé.
2. **Selon le profil** : le poste suivant le plus lourd (perception incrémentale, recherche neuve moins
   chère…). Pas de code compilé pour le planificateur ; pour la géométrie de la perception seulement, et
   seulement si elle domine encore, avec la version Python gardée comme référence de `VERIFICATION`.

## Mesures
Temps d'une nuit au processeur, `main` → branche, les deux lancés ensemble (exception prévue : le
chantier mesure le temps de calcul), 4 processus au plus ; pic de mémoire ; nombre de choix repris.

## Livraison
Commits signés comme d'habitude ; pousse la branche `cout-calcul` sur `origin` (pas `main`). Ce chantier
sera fusionné **en dernier** (après l'appel négocié et les branches Codex qui touchent `deliberation` et
`planification`) : la clé de reprise devra contenir leurs lectures, et la vérification sera refaite sur le
`main` final. Docs : `docs/plan-planificateur.md` (« Coût de calcul »), `docs/etat-dev.md` (« Branche
`cout-calcul`, non fusionnée »). Rapport dans `docs/taches/rapport-cout-calcul.md`.
