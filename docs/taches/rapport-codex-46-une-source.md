# Lot 46 — une source de plus sans capacité nouvelle n'ouvre aucun geste

Branche `codex-une-source`, non fusionnée, base intégration `bafb9b9` ; ancien moteur `42bb9c0`.
Aucun appel au modèle ; aucun coût, prix, borne de nœuds ni scénario modifié.

**Invariant.** Une source de lumière portable de plus, qui n'apporte aucune capacité absente des
sources déjà portées, n'ouvre aucun geste de la recherche : ni prendre, ni demander, ni acheter, ni
saisir sur un porteur (ni donc chercher ce porteur), ni la faire remettre par une aide sur place,
sauf si le but la vise. La règle est commune (`gestes`, `_aide_sur_place`), indépendante d'`emplois` :
la référence de `VERIFIER` l'applique aussi, comme celle des combustibles sans source à recharger.

**Capacité** (`Vue.capacite`), lue de ce que lisent les gestes de lumière (`feu`, `flamme`, `brule`,
la faute) : rang 3 allumée (lumière et flamme), 2 éteinte et chargée, 1 éteinte et vide qui se
recharge de sa substance, 0 rien ; plus « sans faute » (bien d'autrui sans permission). `Vue.couvre` :
allumée couvre tout ; sinon rang au moins égal, même substance au rang 1, sans faute si l'autre l'est.
La candidate est jugée au mieux (acquise par demande : permise). Seules les sources qui ne servent
qu'à y voir (`Vue.sources_seules`) sont concernées ; une source portée `contrarie` ne couvre rien.
`Vue.doublon` applique la règle. Aucune lecture nouvelle hors de `_entrees`.

**Recherches rejouées** (nuit de 1985 rechargée à 8 h, chaque recherche neuve de plus de 200 nœuds
refaite à caches vides sans et avec la règle, et en complète à `REFERENCE` si l'une est bornée) :
mine 480–570, 180 recherches, **0 écart**, nœuds 373 115 → 109 871 (−71 %), CPU 157 → 51 s ;
Rémy `faim` 4 000 bornée → 1 408 épuisée (complète : 5 392, épuisée) ; Josse `feu:poele` à 481,
bornée → plan 15,962 en 416 nœuds, celui de la complète (4 921 nœuds). Auberge 480–570 : 45
recherches, mêmes nœuds, 0 écart.

**Temps sur 12 h** — `42bb9c0`, `bafb9b9` et la branche lancés ensemble, deux processus chacun,
priorité réduite, poste partagé avec une session Codex (bruit ±15 % sur une tranche identique).
Cellules **ancien / base / branche**, secondes CPU ; tranches d'après `cpu_cumule_4h`.

| Nuit | Total | 0–4 h | 4–8 h | 8–12 h | Nœuds (base → branche) | Bornées |
|---|---|---|---|---|---|---|
| Mine 42 tiré | 197,7 / 512,4 / 478,6 | 21,0 / 26,2 / 24,7 | 36,9 / 97,8 / 56,0 | 139,7 / 388,3 / 397,8 | 1 666 715 → 1 083 908 | 108 / 278 / 162 |
| Mine 1985 tiré | 173,7 / 726,7 / 388,8 | 18,5 / 23,6 / 22,4 | 46,6 / 211,7 / 93,2 | 108,5 / 491,2 / 273,1 | 2 257 233 → 642 478 | 4 / 482 / 1 |
| Auberge 42 tiré | 167,2 / 594,1 / 563,5 | 12,8 / 22,5 / 22,8 | 25,1 / 62,1 / 57,7 | 129,2 / 509,3 / 482,7 | 944 982 → 859 036 | 0 / 3 / 0 |
| Auberge 1985 tiré | 152,2 / 313,1 / 323,0 | 13,1 / 19,8 / 20,9 | 27,3 / 69,7 / 72,1 | 111,7 / 223,5 / 229,9 | 483 003 → 479 177 | 8 / 0 / 0 |
| Mine 42 fixe | 197,1 / 541,8 / 259,7 | 16,9 / 28,9 / 26,9 | 37,5 / 130,7 / 64,6 | 142,6 / 382,0 / 168,0 | 1 825 944 → 1 111 572 | 16 / 285 / 151 |
| Mine 1985 fixe | 480,1 / 681,7 / 498,1 | 16,5 / 24,5 / 23,7 | 39,1 / 74,2 / 47,9 | 424,2 / 582,9 / 426,3 | 1 704 078 → 1 138 198 | 56 / 258 / 174 |
| Auberge 42 fixe | 189,7 / 343,8 / 394,9 | 15,3 / 20,5 / 20,9 | 40,3 / 124,0 / 145,0 | 133,8 / 199,1 / 228,8 | 470 767 → 448 632 | 37 / 7 / 1 |
| Auberge 1985 fixe | 197,1 / 428,3 / 427,1 | 16,3 / 19,8 / 19,3 | 23,0 / 52,3 / 57,3 | 157,6 / 356,0 / 350,4 | 755 462 → 718 656 | 3 / 47 / 47 |

Mine, quatre nuits : 2 462,6 → 1 625,1 s (**−34 %**, ×1,43 tiré, ×1,61 fixe) ; encore ×1,55 contre
l'ancien. Auberge : 1 679,2 → 1 708,5 s (+1,7 %, dans le bruit) : la règle n'y élague presque rien.

**Divergences** (`comparer --calcul` base contre branche : 5 nuits sur 8 identiques, recherches
comprises). Les trois autres sont localisées à leur premier appel de recherche différent ; chaque fois
la base atteint sa borne sans plan, la branche trouve exactement le plan de la recherche complète sans
la règle (`REFERENCE`, même coût, mêmes étapes) :

- mine 42 tiré, minute 408, Josse `feu:poele` : base 4 000 nœuds bornée ; branche 422 nœuds,
  plan 13,750 (aller au bureau, payer Bram) ; complète 4 569 nœuds, même plan ;
- mine 1985 tiré, minute 414, Josse `feu:poele` : idem, 13,893 ; complète 4 870 nœuds ;
- auberge 42 fixe, minute 510, Lucien `garder:etable` : base bornée ; branche 3 402 nœuds, rester
  (72,0) ; complète 5 398 nœuds, même résultat.

La suite des nuits diffère donc par des décisions qu'aurait prises la recherche complète.

**Autres vérifications.** Empreintes 2 h (`comparer_bancs --empreintes --reference bafb9b9`, quatre
scénarios × quatre graines) : identiques (chronique, mesures, état final complet). `VERIFIER` et
`spatial.VERIFICATION` 1 sur 2 h, mine et auberge 42 (`empreintes_nuits.py jouer --verifier
--verification 1`) : sans écart ni borne, aucune usurpation ; deux passes (avant et après le plantage
du poste), empreintes identiques entre elles. Cinq tests
(`tests/test_une_source.py`), après rechargement : capacité et couverture ; source pleine demandée
quand la sienne est vide, une vide du même porteur jamais demandée (mine, auberge) ; sa source pleine,
aucune autre acquise, même coût en moins d'états (mine, auberge) ; source visée par le but prise ;
capture réelle de la mine à 8 h : Rémy 4 468 → 1 302 états, Josse 4 946 → 415, base bornée, même
résultat que la complète (4 978 et 6 069 états). Suite complète unique (`tools/tests.py --processus 3`,
priorité réduite) : **1 730 tests, 16 ignorés**, verte, 1 192,7 s.

**Limites.** La règle ne touche que l'acquisition : allumer ou recharger sur place une source non
portée reste offert (une lampe posée éclaire sa salle sans se consumer en main). Le devis d'une part
remise (`part_estimee`) peut encore envisager une seconde source. La couverture est par source, pas
par réunion de sources. Un objet de plus est supposé ne rendre aucun passage possible (charge,
encombrement). Mine : 151 à 174 recherches encore bornées par nuit (autres buts) ; l'auberge ne gagne
rien : son coût est ailleurs (suites prévues : borne exacte des buts qui se tiennent en restant,
départ feutré seulement si un geste sans témoin est découvert, devis vides). Commits non signés : aucune
clé de signature n'est configurée pour ce dépôt sur ce poste. Bruts : `artifacts/une-source/` du worktree.
