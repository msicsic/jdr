# Tâche Codex 64 : ce qu'on a déjà dit à quelqu'un ne se redit pas, quelle que soit la nouvelle

Branche `codex-deja-dit` (elle porte ce fichier, issue de l'intégration **de3e986** : lots 38 à 59 compris), worktree dans
`tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna.

Lot en même temps sur ce poste : 63 (`planification.py`, la mémoire des recherches). Ce lot touche `donjon/social.py`
(`bavarder`, `nouvelles`, `_constats`, `_a_dire`, `recevoir`) et l'esprit ; pas `planification.py`.

Lis `AGENTS.md`, `docs/etat-dev.md` (**« Vérification d'intégration 5c2ce81 », défaut (7)** ; entrées `boucles-pnj`
(« ce qu'on a déjà dit » : `_a_dire`), `codex-constats-partages` lot 55 (sa réserve : mine 2024, cinq avertissements
redits, lampes et soupes homonymes), `codex-soi-meme` lot 35), puis `donjon/social.py`, `donjon/esprits.py` (`croire`,
`memoriser`, mémoire bornée). Bruts : `C:\Users\msics\donjon\artifacts\verif-integ-5c2ce81\extraits.txt` (mine 3,
Josse et Lucien) et `audit-12h\`.

## Le constat
Mine 3 : Josse répète cinq fois à Lucien « Odon semble guetter la porte du bureau » (minutes 14 à 247). Avertissements
redits à l'auberge 0,6 → 2,9 par nuit (audit 5c2ce81) ; le lot 55 en ajoute (mine 2,25 par nuit, dont une ancienne
nouvelle retransmise et deux objets homonymes pris pour le même). La règle « un fait dit l'est jusqu'à ce que sa valeur
change » (boucles-pnj) ne tient donc pas pour toutes les nouvelles : un souvenir sorti de la mémoire bornée, une
intention lue (`intention_lue`) qui se renouvelle, un constat d'un objet homonyme.

## L'invariant
**Ce qu'un PNJ a dit à quelqu'un, il ne le lui redit pas tant que le fait n'a pas changé**, quelle que soit la sorte de
nouvelle (accusation, intention lue, constat, lieu d'un bien), même si son propre souvenir est sorti de la mémoire
bornée : le registre « dit à » est porté par un champ sauvegardé et borné indépendamment, clé par l'identité du fait
(qui, quoi, quel objet par identifiant, valeur) et non par son texte. Une intention lue de nouveau sans changement de
valeur n'est pas un fait nouveau. Pas de cas de Josse ni d'Odon.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : Josse et Lucien (capture mine 3) : un seul avertissement ; un constat
  sur deux objets homonymes distincts : deux nouvelles distinctes, chacune une fois ; un fait qui change de valeur :
  redit une fois ; un souvenir sorti de la mémoire bornée : pas redit.
- Banc rapide (`tools/comparer_bancs.py --reference de3e986`, 4 h, 4 graines, quatre scénarios) : avertissements redits,
  constats confiés, aucune usurpation ni boucle nouvelle ; puis l'audit 12 h de mine 3 et auberge 7, branche seule.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` ou `docs/plan-ouie.md` (là où vit la règle),
`docs/etat-dev.md` (« Branche `codex-deja-dit`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-64-deja-dit.md`.
