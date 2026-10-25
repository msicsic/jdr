# Tâche Codex 75 : un outil n'est pertinent que s'il lève un obstacle entre le PNJ et ce que vise son but

Branche `codex-pertinence-arriere` (elle porte ce fichier, issue de l'intégration **6be0b80** : lots 38 à 72 compris), worktree
dans `tmp-worktrees/`. Lot de coût, demandé par l'utilisateur (« les bancs sont trop lents »). Pas de Luna. **Un seul
poste** : priorité réduite, au plus 3 processus ; mesures de 12 h, trois versions ensemble, **un processus chacune**. Un lot
de certificat d'absence (`_sans_plan`, `_parcours`) peut entrer dans l'intégration pendant ton lot : `git merge
origin/integration` au début si elle a avancé.

Lot en même temps sur ce poste : 73 ou 74 (le récit : `narration.py`, `mj.py`). Ce lot touche `planification.Vue`
(`pertinent`, `verrous`, `agissables`) et les gestes d'acquisition ; pas le récit.

Lis `AGENTS.md`, `docs/etat-dev.md` (« À revoir », volet coût : **P2** ; entrées `codex-une-source` 46,
`codex-capacite-nouvelle` 52 non fusionné (pourquoi il n'a rien gagné), `codex-salles-interet` 62 (diagnostic : 87 % des
états de l'auberge portent des acquisitions préparatoires ; Joss/faim et Tilo/faim bornés), `codex-faim-sans-plan` 63
(diagnostic), `codex-cout-fixe` 71 et `codex-etapes-chainees` 72 (gains de 2 %), et leur contrat), puis
`donjon/planification.py` (`Vue.__init__` : `self.verrous`, `Vue.pertinent` vers la ligne 352-370, `agissables`, `gestes`).

## Le constat
Sur 12 h, graine 1985, l'auberge coûte encore **×5,5** (114 → 610 s au départ tiré, 125 → 593 s fixe) contre `42bb9c0`,
alors que la mine est revenue près de `main`. Le coût de fin de nuit est dans Joss/faim et Tilo/faim, bornées à 4 000
nœuds, et 87 % des états portent des acquisitions préparatoires. Or `Vue.pertinent` rend pertinents **tous** les outils de
choc et de coupe du monde dès qu'une serrure est crue verrouillée quelque part (`self.verrous`), et toutes les clés et
contenants : un PNJ qui veut manger explore « prendre la hache, puis la pioche… » même si rien de verrouillé ne le sépare de
la nourriture.

## D'abord, mesurer
Sur la capture `tests/data/cout-12h/auberge-1985-480.json.gz` (Joss/faim, Tilo/faim) : quels objets non visés par le but
sont acquis dans les états développés, et pourquoi chacun est pertinent (quelle clause de `pertinent`). Si la cause n'est
pas là, dis-la, chiffres à l'appui, et arrête-toi au diagnostic.

## L'invariant
**Un moyen non visé par le but n'est pertinent que s'il peut lever un obstacle sur un chemin entre le PNJ et ce que le but
vise** : couche 0, les objets que le but peut employer (`vises`, vivres, foyers, sources, combustibles) ; couche k+1, ce qui
bloque la couche k (un contenant fermé ou verrouillé qui la contient, une porte verrouillée sur une route vers elle) et les
moyens de le lever (sa clé, ce qui le crochète ou le force), fautes comprises, par une clôture complète sur les
préconditions des gestes ; une seule fonction, calculée une fois par `Vue` et par but ; ce qu'elle lit entre dans
`_entrees` ; `VERIFIER` applique la même règle. Prouve qu'aucun plan n'est perdu (tout geste d'un plan optimal emploie un
moyen de la clôture).

**Contrat** (lots 46, 48, 51) : décisions identiques là où la référence n'atteint pas son plafond ; là où elle l'atteint,
résultat égal à la recherche complète (`REFERENCE`) ; divergences localisées et justifiées ; après bifurcation, mesures.

## Vérification (demandée expressément)
- Tests après rechargement : Joss/faim sur la capture : moins d'états, même résultat que la complète ; un plan qui a
  vraiment besoin d'un outil pour ouvrir le contenant des vivres (forcer ou crocheter) : l'outil reste pertinent ; une porte
  verrouillée sur la route : sa clé reste pertinente.
- Empreintes 2 h (`tools/comparer_bancs.py --empreintes --reference 6be0b80 --processus 3`), quatre scénarios × 4 graines.
- **Temps sur 12 h** : `42bb9c0`, la base et la branche **lancés ensemble**, un processus chacune (`tools/empreintes_nuits.py
  jouer --heures 12 --scenarios mine auberge --graines 1985 --processus 1`, tiré et fixe) ; `comparer --calcul` base contre
  branche, divergences justifiées.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, auberge 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la clôture et sa preuve), `docs/etat-dev.md`
(« Branche `codex-pertinence-arriere`, non fusionnée » ; P2 dans « À revoir »). Rapport d'une page :
`docs/taches/rapport-codex-75-pertinence-arriere.md`.
