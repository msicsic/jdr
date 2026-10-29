# Tâche Codex 287 : conception de la refonte du MJ (moteur qui écrit le mécanique, narration cosmétique)

**Lot de conception seulement : aucun code du jeu, aucun appel à Luna, aucun banc.** Livrable : un document de
conception et un plan de lots, à décider avec l'utilisateur.

## La demande de l'utilisateur (29 octobre)
« Beaucoup des points traités sont en fait mécaniques : le moteur pourrait très bien générer ces phrases (regard méfiant,
nombre de pas…), de façon déterministe. Je penche vers l'approche prise dans la branche `prompt-simplifie` (non
terminée) : la narration est essentiellement cosmétique et ne doit donc pas bloquer la boucle de jeu. Ce qui peut être
généré mécaniquement doit l'être. »

Les lots en attente **176** (contrôle des attitudes), **170** (consignes allégées), **162** (schéma d'audit narratif
invariant) et **171** (faux refus de mesures) sont versés dans cette refonte : dis ce que chacun devient. Le lot **166**
est abandonné.

## À lire
- `AGENTS.md` (contrat du MJ : trois niveaux mécanique / interactif / ambiance), `docs/contrat-mj.md`,
  `docs/plan-migration-mj.md` (revue du 17 octobre, phases 3 et 6 reportées), `docs/plan-prompt.md` (L0 à L8).
- La branche **`origin/prompt-simplifie`** (base `c870c8b`, 20 commits, environ 4 400 lignes, non fusionnée) :
  - `donjon/compilateur.py` : compilation d'intention avec un petit contexte ;
  - `donjon/narrateur.py` : narration d'ambiance a posteriori, en tâche de fond non bloquante, gardes déterministes ;
  - `MJ._echanger_decouple` dans `donjon/mj.py`, le bandeau « Narrateur » de `jeu.py` et de la page web, le fournisseur
    local unifié ;
  - son entrée dans `docs/etat-dev.md` (sur la branche) et ses tests (`test_proto`, `test_narration_thread`,
    `test_schema_compilateur`, `test_prompt_transport`).

  L'intégration a avancé de plus de 220 commits depuis sa base : mesure ce qui a divergé (paroles, refus, audits,
  comptes écrits par le moteur du lot 180).
- Ce que la narration fait aujourd'hui sur l'intégration : `donjon/mj.py`, `narration.py`, `paroles.py`, `consignes.py`,
  la contre-revue de fidélité, l'audit narratif, la portée des ajouts, les explications de refus, les replis.
- Les rapports de mesure Luna : lots 93 (temps par fonction : audit narratif environ 41 % de l'attente, interprétation
  environ 37 %), 95, 116, 141, 153, 162, 165, 168, 170, 171, 176, 180, 216, et la vérification Luna c9459ce
  (`docs/etat-dev.md`, « Où on en est »). Les fils archivés sont dans `C:\Users\msics\donjon\artifacts\bancs-multi\` et
  `artifacts\verif-luna-*\` : **lecture seule**, pour compter et classer, sans rejeu.

## Ce que le document doit établir
1. **Inventaire de la boucle actuelle.** Chaque appel au modèle par tour (interprétation, corrections, contre-revue,
   audit narratif, révisions, explications, replis) : ce qu'il garantit, sa part du temps et des relances (mesurée sur
   les fils archivés), et les familles de refus qu'il produit (justes et faux).
2. **Classement des affirmations affichées au joueur**, par famille : présences, positions, orientation, distances et
   pas, lumière, possessions, comptes, résultats d'action, refus, signes et attitudes perçus, paroles des PNJ, ambiance.
   Pour chacune :
   - **mécanique**, déjà écrite par le moteur ou à écrire de façon déterministe ;
   - **interactive** ;
   - **cosmétique** (ambiance libre).

   Dis, pour chaque famille mécanique, quelle donnée du moteur suffit à écrire la phrase, et ce qui existe déjà
   (bilan des présences, phrases de comptes du lot 180, rendu des résultats, signes du lot 21/3c).
3. **Les répliques des PNJ**, point dur : qui fixe le contenu (opération typée, issue du moteur) et qui fixe la
   formulation ? Quel contrôle reste nécessaire si Luna formule une réplique dont le moteur a fixé le sens ? Compare au
   moins deux options.
4. **Architecture cible.** Boucle de jeu :
   1. la saisie ;
   2. la compilation d'intention (le seul appel bloquant) ;
   3. la validation par le moteur ;
   4. le rendu mécanique déterministe ;
   5. la sauvegarde et l'affichage ;
   6. la narration d'ambiance en fond.

   Dis ce que la narration a le droit d'affirmer. Une sortie qui échoue aux gardes déterministes est **jetée, pas
   relancée**. Dis comment elle est enregistrée avec son lieu (contrat de l'ambiance). Évalue ce que la branche
   `prompt-simplifie` apporte de réutilisable, ce qu'il faut reprendre et ce qu'il faut écarter.
5. **Contrat du MJ.** Si la refonte change le contrat écrit dans `AGENTS.md` (par exemple, plus d'audit sémantique de
   l'ambiance, ou une garantie seulement déterministe), propose la nouvelle formulation, **marquée comme décision à
   l'utilisateur**. Dis quelles garanties actuelles disparaissent ou se renforcent.
6. **Sort des audits et lots en attente** : contre-revue de fidélité, audit narratif, portée des ajouts, explications ;
   lots 176, 170, 162, 171. Pour chacun : supprimé, remplacé par une phrase du moteur, conservé ou déplacé.
7. **Plan de lots.** Lots de 30 à 45 minutes, un invariant chacun, dans l'ordre. Pour chacun : fichiers touchés,
   critère de mesure Luna (appels et secondes par tour, relances, refus, replis, contre la référence en cache) et
   tests. Mets en tête les familles mécaniques les plus coûteuses aujourd'hui. Prévois la compatibilité `gpt-6-luna`
   (forfait ChatGPT, WebSocket) et le fournisseur local.
8. **Risques et questions à l'utilisateur**, numérotés, avec ta recommandation pour chacun.

## Contraintes
- Lecture et rédaction seulement : aucun fichier sous `donjon/`, `tests/` ou `tools/` modifié. Les petits scripts de
  comptage vont dans `C:\Users\msics\donjon\artifacts\refonte-287\`, jamais dans le dépôt.
- **Poste : le laptop.** Une vérification d'intégration (lot 284) y tourne : un seul processus Python léger à la fois.
- Ne fusionne rien, ne rebase pas `prompt-simplifie`.

## Livraison
- Branche `codex-conception-refonte-mj` poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur).
  Si la poussée échoue, laisse le commit local, donne son hash et l'erreur exacte.
- Document `docs/conception-refonte-mj.md`.
- Rapport d'une page `docs/taches/rapport-codex-287-conception-refonte-mj.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.
