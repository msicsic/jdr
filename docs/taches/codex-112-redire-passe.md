# Tâche Codex 112 : une réplique ne contredit pas ce que son locuteur a déjà dit au joueur

Petit lot (`AGENTS.md`, « Rythme des lots »). **Luna disponible** pour une passe de contrôle, copies seulement ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul poste** :
priorité réduite, au plus 2 processus de calcul, Luna en 4 exécutions au plus ; d'autres lots tournent (lot 110 dans `echanges`/
`propositions`/`deliberation` ; lot 111, vérification Luna sans code). Ce lot touche le dossier et le contrôle du récit (`mj.py`,
`narration.py`). Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat (passe Luna du lot 102, `soir-noir`)
Partie : `C:\Users\msics\donjon\artifacts\n3-soir-noir-lot102\20261026-022930-37884\lot-r1\…-soir-noir.json`. Tour 2 : la voix
répond « C'est Ilse. Qui va là ? ». Tour 4 : Corvus se dit Brune, la voix le démasque. Tour 5, « je demande à la voix comment elle
s'appelle » → affiché : **« Je t'ai déjà dit que je ne te dirai pas qui je suis. »** Le refus de se nommer peut être légitime (méfiance
après l'imposture), mais la réplique affirme un fait passé faux (elle a dit son nom au tour 2) ; l'audit l'a admise.

## L'invariant
**Une parole d'un PNJ est un fait mécanique quand elle affirme ce qu'il a déjà dit ou fait** (« je t'ai déjà dit… », « comme je
te l'ai dit… ») : elle doit être compatible avec ce que le moteur a enregistré des échanges entre lui et Corvus (paroles entendues,
présentations, refus). Le dossier du récit porte ce que ce locuteur a déjà dit à Corvus dans la scène (en références publiques),
et le contrôle refuse une affirmation contraire avec un `attendu` qui cite ce qui a été dit ; le contenu de la réponse décidée par
le moteur (ici : refus de se nommer) reste libre de forme. Pas de mot-clé de phrase ni d'exception de scénario : un contrat commun
du dossier et de l'audit.

## Vérification
- Tests après rechargement avec MJ simulé : le cas réel (tour 5) refusé puis corrigé en un refus compatible (« je ne te le
  redirai pas » ou équivalent sans affirmation fausse) ; un autre cas de même nature (un PNJ qui affirme avoir déjà refusé une part
  qu'il a en fait servie) ; une réplique qui rappelle exactement une parole réellement dite toujours admise.
- Luna, une passe de `soir-noir` et `soir-voix` : la contradiction ne revient pas ; appels et secondes par tour.
- Tests ciblés ; suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche `codex-redire-passe`, non
fusionnée »). Rapport d'une demi-page : `docs/taches/rapport-codex-112-redire-passe.md`.
