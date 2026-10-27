# Tâche Codex 170 (plan prompt, L6) : des consignes d'interprétation sans doublons

Lot de 30 à 45 minutes (`AGENTS.md`). **Poste : le laptop** (`C:\Users\msics\donjon`, Luna connectée ;
`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`, copies seulement : cadre normal du dépôt, voir `AGENTS.md`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Aucun autre lot sur ce poste ; deux sur le PC fixe (agendas, audit narratif) : au
plus 2 processus de calcul, Luna en 2 exécutions au plus, priorité réduite. Ce lot touche le texte de `consignes.py` et les `REGLES`
d'`artisanat`, `franchissement`, `obstacles`, `espace`, `localisation`, et `REGLES_PAROLE`/`REGLE_NARRATION` de `mj.py` si elles
y sont définies, avec leurs tests ; **pas** `narration.py` (lot 169), la logique de `mj.py`, le schéma, `sources.py`, les
fournisseurs. **Bruts dans `C:\Users\msics\donjon\artifacts\consignes-170\`, jamais dans le worktree.** Si une revue automatique
bloque Luna ou la poussée, termine le reste, commite localement et écris la commande exacte dans
`C:\Users\msics\donjon\artifacts\consignes-170\luna-a-jouer.txt`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une
ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, **`docs/plan-prompt.md`** (L6), les rapports des lots 149 (L0 : socle 33 335 caractères), 161 (L3 : toutes les
règles désormais permanentes dans le socle) et 165 (vérification Luna 227c496 : relances 24 → 41), `docs/contrat-mj.md`, puis les
consignes d'interprétation telles qu'assemblées aujourd'hui (`mj._echanger`).

## L'invariant
**Chaque règle d'interprétation est dite une seule fois, au bon endroit ; aucune règle n'est perdue.** Retire les doublons entre
le socle (`INTERPRETATION`) et les règles devenues permanentes au lot 161 (atelier, franchissement, obstacles, espace, parole,
localisation), et les barèmes que le moteur vérifie déjà et renvoie en `attendu` (durées, DD détaillés) **seulement si** une
règle équivalente reste lisible ; garde les règles qui évitent un refus. Aucune règle nouvelle, aucun exemple propre à un objet.
Les consignes restent invariantes (lot 161) et le contrat propre pour Luna et le fournisseur local.

## Vérification
- Test : liste des règles (une phrase-clé par règle) présente une seule fois après le lot ; consignes identiques d'un tour à
  l'autre ; deux scènes rejouées par MJ simulé, état et rendu inchangés.
- `tools/mesure_prompt.py` : taille des consignes avant/après.
- Luna, **deux passes** des quatre bancs de référence et de `atelier`, `noms-dialogue`, `soir-appel`, `sous-obstacle-relais`,
  `poser-sol-relais` ; référence `cdaf371` relue du cache ; appels et secondes par tour MJ, relances, refus, replis, jetons cachés ;
  critère du lot 95 sur les refus.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-consignes-degraissees` poussée (pas `main`).
`docs/plan-prompt.md` (L6), `docs/etat-dev.md` (« Branche `codex-consignes-degraissees`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-170-consignes-degraissees.md`.
