# Tâche Codex 102 : ne pas percevoir n'est pas constater une absence (le noir)

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Luna disponible** : copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth` ; `tools/banc_multi.py --connexion chatgpt`. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** : priorité réduite, au plus 2 processus de calcul, Luna en
4 exécutions au plus ; d'autres lots tournent (coût du planificateur ; lot 101 dans le garde lexical de méta-langage : n'y touche
pas). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat (lots 79 et 99, persistant)
`signes-noir`, passe 1, saisie n°2 : le MJ affiche « aucune des deux n'est ici » alors que Corvus, Ilse [2,4] et Brune [4,5] sont
tous dans l'antichambre rechargée ; l'audit l'admet (`neutre`, portée `aucune`), deux appels. L'autre passe répond justement
(« l'obscurité ne te permet pas de la distinguer »). Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-b0042c9\`
(`constats.md`, `preuves-incidents.json`), et le rapport du lot 79. Le lot 40 a introduit `perception.objets_visibles` pour
admettre une absence **dans la vue courante** ; dans le noir, la vue est vide.

## L'invariant
**Une absence affirmée est une affirmation mécanique** (présence des PNJ, objets) : elle n'est admise que si une perception du
moteur l'établit (vue éclairée de la salle, fouille, écoute exécutée…), jamais du seul fait que Corvus ne perçoit rien. Dans le
noir, ne pas voir quelqu'un établit qu'on ne le voit pas, pas qu'il n'est pas là ; ce qu'on entend (voix, pas, souffle selon
l'ouïe commune) reste une perception. Le dossier de l'audit doit porter cette distinction (ce que la vue couvre : salle éclairée
ou non, portée) pour que l'absence non établie soit refusée avec un `attendu` qui dit ce qui est perçu ; corrige la règle commune
(dossier de perception de l'audit, classement de la portée), pas une phrase ni un scénario.

## Vérification
- Tests après rechargement avec MJ simulé : le cas réel (deux personnes présentes dans le noir) refusé puis corrigé en « tu ne
  les vois pas » ; un objet présent dans une salle noire, même règle ; une absence établie par une vue éclairée toujours admise ;
  une absence établie par une fouille exécutée toujours admise.
- Luna, une passe de `signes-noir`, `soir-noir`, `atelier` (références du lot 99 en cache) : la fausse absence ne revient pas ;
  appels et secondes par tour.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-absence-noir`, non
fusionnée »). Rapport d'une demi-page : `docs/taches/rapport-codex-102-absence-noir.md`.
