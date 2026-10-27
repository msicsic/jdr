# Tâche Codex 166 (plan prompt, L7) : catalogues d'écriture et surfaces génériques à la demande

Lot de 30 à 45 minutes (`AGENTS.md`) ; **livraison partielle permise** (catalogues d'abord, surfaces ensuite). **Poste : le laptop**
(`C:\Users\msics\donjon`, Luna connectée ; `SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal du dépôt,
voir `AGENTS.md`). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. Aucun autre lot sur ce poste ; une vérification Luna
tourne sur le PC fixe : au plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche l'assemblage
des `faits` dans `mj._echanger` (catalogues `descriptions_a_completer`, `connaissances_a_completer`, `profil_joueur_a_completer`,
`faits_narratifs_proposables`), les catalogues eux-mêmes (`faits_locaux`, `connaissances`, `profil_joueur`, `complements`) et la
projection des surfaces génériques de salle, avec leurs tests ; **pas** `consignes.py` au-delà d'une phrase sur ces catalogues,
`narration.py`, `deliberation.py`/`planification.py` (lot 163). **Bruts dans `C:\Users\msics\donjon\artifacts\faits-166\`,
jamais dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décision 3, L7), `docs/contrat-mj.md` (ambiance ciblée matérialisée, niveaux
interactifs), les rapports des lots 149 (L0 : catalogues et surfaces, plafond brut 1 010 978 caractères cumulés), 154 (Luna
proposait `antichambre_sol`/`cour_sol` comme destination) et 158/161 (L2 : un mode sans catalogue est refusé avec `attendu`).

## L'invariant
**Les catalogues d'écriture et les surfaces génériques (murs, sol, plafond d'une salle) ne sont envoyés au MJ que lorsqu'ils
servent : un catalogue quand la saisie ou le tour peut l'employer (sinon le mode correspondant reste refusé avec `attendu`, comme
depuis L2) ; une surface quand elle est ciblée par la saisie ou porte un détail établi.** Le contrat « un élément d'ambiance
ciblé est matérialisé par le moteur ou déclaré non manipulable » reste tenu ; aucune entité perçue n'est cachée au MJ ; aucune
règle propre à un objet ou un scénario. Choisis un critère d'usage commun, déterministe et testable (pas de mot-clé de saisie
propre à un exemple) ; si un critère sûr manque pour un catalogue, laisse-le et dis-le.

## Vérification
- Tests console/MJ simulé après rechargement : examen d'un mur sans détail (surface matérialisée ou déclarée non manipulable),
  détail établi sur le sol puis ciblé, description d'un objet à compléter encore possible, poser au sol sans surface proposée ;
  état et rendu inchangés.
- `tools/mesure_prompt.py` : taille de `faits` par voie avant/après sur les mêmes scènes ; part des catalogues et surfaces.
- Luna, **deux passes** des quatre bancs de référence et de `atelier`, `luna-restes-ambiance`, `poser-sol-relais`, `soir-appel` ;
  référence `cdaf371` relue du cache ; appels et secondes par tour MJ, jetons cachés, relances, refus, replis ; critère du lot 95.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-faits-a-la-demande` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/plan-prompt.md` (L7), `docs/etat-dev.md` (« Branche `codex-faits-a-la-demande`, non
fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-166-faits-a-la-demande.md`.
