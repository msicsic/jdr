# Tâche Codex 347 : conception, menace ou échéance négociée

Lot de conception seul, **sans code**. A5 (mandat et autorité) est presque fini : lots 248 à 341 fusionnés, 306
(données du hameau) en attente. La décision du 2026-10-29 sur le lot 288 (section 8 de
`docs/conception-valeur-llm.md`, question 5) dit : après A5, choisir **menace ou échéance négociée** à partir d'un
cas de jeu, sans ouvrir les deux dans un même lot « dialogue complexe ».

Lis `AGENTS.md`, `docs/etat-dev.md` (court), `docs/plan-agendas.md` (sections A6 à A8 et décisions),
`docs/plan-relations.md` (propositions 3e, avis 3f), `docs/plan-force.md` (4b à 4f), `docs/conception-valeur-llm.md`
(sections 4 à 8) et le rapport 245. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, ne le
lis pas en entier.

## Ce qu'on attend
1. **Deux à quatre cas de jeu réels**, tirés des scénarios existants (Relais, crue, hameau, mine, auberge) et de
   nuits ou captures archivées si utile : une situation où un PNJ ou le joueur gagnerait à menacer (« rends-le ou
   je… »), et une où il gagnerait à négocier une échéance (« je te paie demain », « garde la torche jusqu'à
   minuit »). Pour chaque cas : ce qui se passe aujourd'hui, ce qui manque, ce que le joueur ferait.
2. **Les briques existantes** que chacune réutiliserait (propositions et contreparties, engagements et échéances
   d'`agendas`, relations peur/rancune/dette, force 4b–4e, jugement commun, avis, parole typée, U-P/U-C) et ce qui
   manque vraiment. Une menace doit rester une parole : elle n'établit rien de vrai ; sa crédibilité se juge sur les
   croyances de celui qui l'entend (force crue, témoins, précédents), sans lire la volonté privée du menaçant.
3. **Une recommandation** : laquelle des deux d'abord, et pourquoi, au regard de la richesse des PNJ et du jeu du
   joueur ; son invariant ; un découpage en lots d'un invariant chacun (30 à 45 minutes), avec fichiers prévus,
   épreuves et mesures. Ce qui touche le MJ suit le contrat du MJ (`AGENTS.md`) : contenu typé, rendu par le moteur.
4. Les questions à trancher par l'utilisateur, avec ta recommandation pour chacune.

## Contraintes
**Poste : le PC fixe.** Documentation seule : aucun fichier sous `donjon/`, `tests/` ou `tools/` modifié ; un
processus Python léger à la fois si tu dois lire des archives. Ni Luna, ni banc, ni suite.

## Livraison
- Branche `codex-conception-menace`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- `docs/conception-menace-echeance.md` (la conception) et un rapport d'une page
  `docs/taches/rapport-codex-347-conception-menace-echeance.md` ; entrée « non fusionnée » de 8 lignes au plus dans
  `docs/etat-dev.md`, section « Lots non fusionnés ».
- Bruts éventuels dans `C:\Users\msics\donjon\artifacts\menace-347\`.
- Termine par `LOT TERMINÉ` ou `QUESTION : …`.
