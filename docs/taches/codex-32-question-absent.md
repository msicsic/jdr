# Tâche Codex 32 : une question sur une personne connue absente va au MJ

Branche `codex-question-absent` (elle porte ce fichier, issue de l'intégration **2590c4a**), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). **Luna disponible**
(`SEUIL_AUTH` vers le coffre du dépôt principal ; copies seulement).

Lis `AGENTS.md`, `docs/contrat-mj.md`, `docs/etat-dev.md` (lot 27 `codex-nom-non-relie` et sa fusion, avec le
correctif 2917a62 `commandes.perception_nommee`), `docs/taches/rapport-codex-27-nom-non-relie.md`, puis
`donjon/noms.py` (`verifier_saisie`, `verifier_nom`), `donjon/commandes.py` (`analyser`, `faisabilite`,
`PERCEPTIONS`, `perception_nommee`), `jeu.py`, `donjon/mj.py` (`echanger`).

## Le constat (vérification Luna de l'intégration, 3b6415b, 2 passes)
Le garde du lot 27 refuse localement toute saisie qui nomme une personne reliée mais absente, questions
comprises : `signes-guet` « Que fait Brune ? » et « Que fait Gorm en ce moment ? », `signes-noir « Ilse a-t-elle
peur de Brune ? » → « Tu ne vois pas Brune d'ici. », 0 appel, 2/2. Le texte est vrai, mais il ne répond plus
avec ce que Corvus sait (sur `main` : les pas entendus en dessous, les signes reçus). Fils :
`C:\Users\msics\donjon\artifacts\verif-luna-3b6415b\integration-r{1,2}\*signes-guet.json`, `*signes-noir.json`.

## L'invariant
Le refus local d'une personne **reliée** mais hors de vue vaut pour ce qui l'atteindrait : un geste, une parole
qui lui est adressée, une perception qui la vise (le refus du moteur avec sa cause, `perception_nommee`). Une
**question** du joueur sur cette personne (ce qu'elle fait, ce qu'elle ressent, où elle est) va au MJ, qui ne
répond qu'avec ce que Corvus sait (souvenirs, bruits, signes reçus), sans rien inventer d'invisible. Un nom
**non relié** reste refusé pour tout, questions comprises (lot 27, inchangé). Une règle commune, par la nature de
la saisie (question, geste, parole), jamais par mot ou par exemple ; dis comment la question est reconnue et ce
qui reste sémantique.

## Vérification (minimale)
- Tests après rechargement (`tests/test_question_absent.py`), MJ simulé : « Que fait Brune ? » (Brune reliée,
  absente) va au MJ, une fois ; « je pousse Brune » absente : refus local, 0 appel ; « observer Ilse » dans le noir :
  refus du moteur « cette personne », 0 appel ; « Que fait Aubin ? » non relié : refus du lot 27, 0 appel ; un
  autre cas de même nature pour chacun.
- Luna, **une passe** : `signes-guet`, `signes-noir`, `echanges`, `noms-dialogue` (`tools/banc_parties.py --fil`) ;
  les questions répondues avec ce que Corvus sait, aucune fuite du guet caché, rien d'invisible affirmé ;
  « je pousse Aubin » et « observer Ilse » toujours à 0 appel.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/contrat-mj.md`, `docs/etat-dev.md` (« Branche
`codex-question-absent`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-32-question-absent.md`.
