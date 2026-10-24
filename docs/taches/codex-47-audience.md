# Tâche Codex 47 : l'audience d'une parole sans destinataire nommé se fixe par une seule règle

Branche `codex-audience` (elle porte ce fichier, issue de l'intégration **60da18c** : lots 38 à 44 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un invariant,
vérification minimale, rapport d'une page. **Luna disponible sur ce poste** (`SEUIL_AUTH` vers le coffre du dépôt
principal ; copies seulement).

D'autres lots tournent en même temps (45 : `deliberation.py`, `echanges.py` ; 46 : `planification.py`). Ne touche
pas à ces fichiers.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-luna-noms`, `parole-corrections` « Répondre à la cantonade »,
`codex-luna-restes`, `codex-question-absent` lot 32), `docs/plan-ouie.md` (« Paroles », « Corrections de la
parole »), `docs/contrat-mj.md`, puis `donjon/paroles.py` (`analyser`, `destinataires`, `_vocatifs`, `repondants`),
`donjon/mj.py` (choix d'audience proposé par Luna, contre-revue de fidélité, message « Précise à qui tu
t'adresses… »). Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-8443458\relecture.txt` (`noms-dialogue` n° 1,
`soir-appel` n° 2, `echanges`, les quatre parties) et les fils dans `20261024-172130-42188\`.

## Le constat (vérification Luna d'intégration 8443458, deux passes ; connu depuis `codex-luna-restes`)
« est-ce que quelqu'un a du bois ? », Aubin en face, Brune et Ilse présentes, une voix à l'ouest : sur `main`, dite
« à tous » ou « Tu dis : … » et chacun répond (4 parties sur 4). Sur l'intégration, `noms-dialogue` passe 1 : Luna
propose deux fois Aubin seul, la contre-revue refuse, et **le joueur lit « Précise à qui tu t'adresses et ce que tu
veux lui dire. »** ; relances aussi dans `soir-appel` (passe 2) et `echanges` (deux passes). Le choix d'audience
reste sémantique et tiraillé entre la règle du moteur (« sinon celui qui est en face ») et le sens de la question.

## L'invariant
**L'audience d'une parole sans destinataire nommé se fixe par une seule règle commune, et le joueur ne lit jamais
« Précise à qui tu t'adresses » quand cette règle donne une audience.** Trouve où se contredisent la règle du moteur
(`destinataires`, « celui d'en face »), la cantonade de `repondants` et la contre-revue, et fais-en une seule
décision : par exemple, qui l'audience comprend quand la parole n'interpelle personne, et ce que la contre-revue
peut encore refuser. Pas de liste de mots (« quelqu'un », « tout le monde ») ni de cas de la question du bois : la
règle porte sur la forme d'adresse (vocatif, nom, personne en face, aucune) et sur ce que le moteur sait des
présents et des voix audibles. Si un mot de la saisie doit être lu, qu'il le soit par l'analyse commune de la parole,
avec un test qui montre la même règle sur une autre formulation.

## Vérification (minimale)
- Tests après rechargement, chaîne complète avec MJ simulé : le cas réel (Relais, Aubin en face, trois présents et
  une voix) ; un autre de même nature (auberge ou mine, une question sans destinataire nommé, quelqu'un en face) ;
  un cas qui doit rester individuel (vocatif ou nom), et la contre-revue qui refuse encore une audience contraire
  aux mots ; jamais le message « Précise à qui… » quand la règle donne une audience.
- Luna, **une passe** : `noms-dialogue`, `soir-appel`, `echanges`, `relais`, `tools/banc_multi.py`, référence `main`
  lue du cache (voir le rapport du lot 40 pour lancer la référence avec son outil historique) ; appels par tour,
  textes affichés pour la question du bois.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-ouie.md` et `docs/contrat-mj.md` (la règle d'audience),
`docs/etat-dev.md` (« Branche `codex-audience`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-47-audience.md` (cause, invariant, fonctions, mesures, limites).
