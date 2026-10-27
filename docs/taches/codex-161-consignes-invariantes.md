# Tâche Codex 161 (plan prompt, L3) : des consignes d'interprétation qui ne dépendent pas du tour

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le laptop** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement). Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
Une suite complète tourne sur ce poste (`.worktrees/integration`) : au plus 2 processus de calcul, Luna en 2 exécutions au plus,
priorité réduite. Ce lot touche `consignes.py`, les `REGLES` d'`artisanat`, `franchissement`, `obstacles`, `espace` et
l'assemblage des consignes dans `mj._echanger`, avec leurs tests ; **pas** `narration.py` (lot 162, audit narratif), ni le schéma
(L2 fait), `sources.py`, les fournisseurs. **Bruts dans `C:\Users\msics\donjon\artifacts\consignes-161\` (dépôt principal), jamais
dans le worktree.** Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (décisions 1, 6, L3), les rapports des lots 149 (L0 : consignes changées 42/113
appels d'interprétation), 152 (dossiers à portée) et 158 (L2), `docs/contrat-mj.md`, puis `mj._echanger` (instructions
`INTERPRETATION` + `REGLES_ATELIER`, `REGLES_FRANCHISSEMENT`, `REGLES_OBSTACLES`, `REGLES_ESPACE` ajoutées si leur dossier
existe, `REGLES_PAROLE`, `REGLE_NARRATION`, `REGLES_LOCALISATION`, le bloc du déplacement, les phrases de `retour_moteur`).

## L'invariant
**Les consignes d'interprétation sont les mêmes à chaque appel d'une partie ; ce qui dépend du tour (dossiers, retour du
moteur, relance) est dans l'entrée, jamais dans les consignes.** Les règles d'atelier, de franchissement, d'obstacles et
d'espace deviennent une partie concise et permanente du socle, qui renvoie au dossier quand il est présent ; les phrases
conditionnelles sur `retour_moteur` et les refus passent dans l'entrée (comme la consigne de révision du lot 150). Pas de
nouvelle règle de jeu, pas d'exemple propre à un objet ; on peut condenser les doublons évidents avec le socle, le gros
dégraissage restant à L6. Contrat propre pour Luna et le fournisseur local.

## Vérification
- Test : sur deux scènes rejouées par MJ simulé (Relais avec obstacle proche, atelier avec établi proche, puis éloignés), les
  consignes d'interprétation sont identiques d'un tour à l'autre et entre les scènes ; état et rendu après rechargement
  inchangés ; le retour du moteur et la relance sont bien dans l'entrée.
- `tools/mesure_prompt.py` : taille et variations des consignes avant/après (base : 42/113 changements).
- Luna, **deux passes** des quatre bancs de référence et de `atelier`, `noms-dialogue`, `soir-appel`, `sous-obstacle-dessous` ;
  référence `cdaf371` relue du cache ; appels et secondes par tour MJ, jetons cachés par voie et `usage.attribution`, relances,
  refus, replis ; critère de refus du lot 95.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-consignes-invariantes` poussée (pas `main`).
`docs/contrat-mj.md` si la règle change, `docs/plan-prompt.md` (L3), `docs/etat-dev.md` (« Branche
`codex-consignes-invariantes`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-161-consignes-invariantes.md`.
