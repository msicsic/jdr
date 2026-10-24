# Tâche 46 : une seconde source de lumière sans capacité nouvelle n'ouvre aucun geste

Branche `codex-une-source` (elle porte ce fichier, issue de l'intégration **bafb9b9** : lots 38 à 43 compris).
Lot de coût, demandé expressément par l'utilisateur (« les bancs sont trop lents »). Pas de Luna.

Lis `AGENTS.md`, `docs/etat-dev.md` (entrées `codex-cout-12h` lot 38, `codex-trajet-estime` lot 30, `codex-lampes`,
`codex-lampes-suite`, `planif-rapide` : « chaque but dit ce qu'il peut employer, et l'on ne porte que ce qui peut le
servir »), `docs/plan-planificateur.md` (« Lumière », « Lumière employée », borne du lot 38), puis
`donjon/planification.py` (`Vue.pertinent`, `emplois`, `gestes` : prendre, demander, acheter, prise sur un porteur ;
`_entrees`, `VERIFIER`, `REFERENCE`, `BORNES`).

## Le diagnostic (mesuré sur l'intégration, graine 1985, 12 h ; bruts dans le scratchpad de la session Claude,
`cout2/`)
En fin de nuit, 94-95 % du temps du planificateur est dans des recherches neuves, dont 68-88 % **sans plan**, qui
rendent le même résultat que la précédente. Rémy `faim` (mine) n'a aucun plan : 42bb9c0 épuisait l'espace en
1 461 états (0,22 s) ; l'intégration atteint la borne de 4 000 nœuds à chaque fois sur 5 392 états (1,5 s), donc
sans certificat d'absence, et le refait. Josse `feu:poele` 2 661 → 5 778 états. **88 % des états portent au moins
deux sources de lumière portables** ; 63 inventaires différents contre 32 sur 42bb9c0. Prototype : interdire une
seconde source portable (pas de seconde prise, demande ni achat, sauf si le but la vise) : nœuds −42 % (Rémy
16 000 → 1 867, Josse 16 000 → 1 230), fenêtre 480-570 de la mine −78 %, **aucun résultat changé sur 69 rejeux** ;
sur les 23 recherches bornées de 480 à 495, la recherche complète à 60 000 nœuds donne exactement le résultat du
prototype (même plan à 15,962 pour Josse, aucun plan pour Rémy, ~5 400 → 500 états). Auberge : ≈ 0.

## L'invariant
**Une source de lumière portable de plus qui n'apporte aucune capacité absente des sources déjà portées (allumée,
chargée, rechargeable, de ce combustible) n'ouvre aucun geste dans la recherche : on ne la prend, ne la demande, ne
l'achète ni ne la saisit sur un porteur, sauf si le but la vise.** Elle prolonge la règle commune « on ne porte que
ce qui peut servir le but » (les combustibles depuis le lot Q), dans la restriction des `emplois`, pour que la
recherche de référence de `VERIFIER` applique la même règle. Définis « capacité » une fois, sur ce que lisent les
gestes de lumière (pas une liste d'objets). Ne change aucun coût, prix, borne de nœuds ni donnée de scénario.

Décisions : identiques là où la recherche actuelle n'est pas bornée (prouve-le par les empreintes) ; là où elle
l'est, compare au résultat de la recherche complète (`REFERENCE`) : le résultat du lot doit l'égaler.

## Vérification (demandée expressément)
- Tests après rechargement : Rémy et Josse (capture `tests/data/cout-12h/mine-1985-480.json.gz`) : moins d'états,
  même résultat que la recherche complète ; un cas où le but vise une source (une lampe éteinte à rallumer, une
  source chargée quand la sienne est vide) : la seconde source reste prise ; un cas de même nature à l'auberge.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference bafb9b9`), quatre scénarios × 4 graines :
  identiques (sinon chaque écart expliqué par une recherche bornée et comparé à `REFERENCE`).
- **Temps sur 12 h** : `42bb9c0`, la base `bafb9b9` et la branche **lancés ensemble**
  (`tools/empreintes_nuits.py jouer --heures 12 --scenarios mine auberge --graines 42 1985 --processus 2` par
  version), CPU total et par tranche de 4 h, nœuds, recherches bornées ; `comparer --calcul` base contre branche :
  chaque divergence localisée et justifiée par une recherche bornée.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés si la configuration le permet (sinon le dire), branche poussée (pas `main`).
`docs/plan-planificateur.md` (la règle), `docs/etat-dev.md` (« Branche `codex-une-source`, non fusionnée »).
Rapport d'une page : `docs/taches/rapport-codex-46-une-source.md` (invariant, fonctions, temps par tranche, nœuds,
divergences, limites). Suites prévues, hors de ce lot : borne exacte des buts qui se tiennent en restant
(RESTER × plancher de pression), départ feutré seulement si un geste sans témoin est découvert, devis vides.
