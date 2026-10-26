# Tâche Codex 124 (3f) : l'avis du joueur, par la parole typée

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). **Poste : le PC fixe** (`C:\Users\msics\donjon`, Luna connectée).
Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste (vérification Luna 123,
diagnostic 125) : au plus 2 processus de calcul, priorité réduite ; Luna en 2 exécutions au plus. Ce lot touche `paroles.py`,
le MJ (`mj.py`, `consignes.py`, schémas) et la réception dans `social.py`/`esprits.py` si besoin ; **pas** `pnj_propositions.py`,
`echanges.py` (lot 122 sur l'autre poste) ni `planification.py`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-relations.md` (§ 7.3 les avis, § 7.4 les disputes, 3f), les rapports des lots 80, 88, 108 et **121**
(disputes), puis `donjon/social.py` (avis, `faire_entendre`, `_contradiction`, `_disputer`), `donjon/esprits.py`
(`prevision`, `poids_source`, `recevoir_prevision`), `donjon/eau.py` (`estimation`, `attendue`), `donjon/paroles.py`
(`CHAMPS_CONTENU`, `SENS_CONTENU`, validation des contenus typés).

## Ce qui manque
Les PNJ se disent leurs avis de menace d'eau et se disputent (lots 80, 88, 121). Le joueur, lui, n'a aucun contenu typé pour
dire « l'eau va gagner le refuge » ou « non, la galerie ne risque rien » : Luna en fait au mieux un `propos`, que personne ne
reçoit comme un avis, et qui ne peut ni convaincre ni ouvrir une dispute.

## L'invariant
**L'avis du joueur passe par le même contrat que celui d'un PNJ.** Contenu typé `avis` (lieu cité par sa référence publique,
menace oui/non), contrôlé par le moteur comme les autres contenus (`attendu` si le lieu est inconnu de Corvus ou le prédicat
hors de ce que le moteur sait évaluer). Sa **conviction** vient de ce que Corvus a perçu de l'eau (même estimation que pour
un PNJ, sans lire le niveau caché) ; sans observation, conviction minimale (deviné). Chaque auditeur qui saisit les mots
le reçoit par `recevoir_prevision` (source « dit par Corvus », confiance et affection envers lui) ; un auditeur plus convaincu
du contraire ouvre la dispute du lot 121, joueur compris, avec ses suites (témoins, parti pris, dispute perdue). Rien n'est
établi comme vrai : une parole établit qu'elle a été dite (contrat du MJ). Le registre des faits dits (lot 108) empêche la
redite. Aucun mot-clé ni règle de scénario ; seul prédicat : la menace d'un lieu.

## Vérification
- Tests après rechargement, MJ simulé puis console : Corvus dit à Gorm que la conduite sera noyée ; Gorm sans prévision
  l'adopte (doute selon sa confiance) ; Gorm qui a vu l'eau baisser le contredit, dispute et témoins ; Corvus sans
  observation : conviction minimale ; lieu inconnu ou prédicat hors moteur : `attendu`, rien d'enregistré ; second auditeur.
- Luna, **une passe** : un script court ajouté sous `tests/data/bancs/` (crue) avec trois saisies (avis à un PNJ, avis
  contredit, avis à la cantonade) ; typage du premier coup ou non, appels par tour, aucun faux refus affiché.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée sur ce poste (sinon le dire), branche poussée (pas `main`). `docs/plan-relations.md`,
`docs/contrat-mj.md` si le contrat change, `docs/etat-dev.md` (« Branche `codex-avis-joueur`, non fusionnée »). Rapport d'une
page : `docs/taches/rapport-codex-124-avis-joueur.md`.
