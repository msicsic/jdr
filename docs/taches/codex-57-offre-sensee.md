# Tâche Codex 57 : un PNJ n'offre que ce qu'il accepterait de céder, et ne redit pas une offre refusée

Branche `codex-offre-sensee` (elle porte ce fichier, issue de l'intégration **c592d68** : lots 38 à 55 compris),
worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots »). Pas de Luna.

Lots en même temps : 58 sur ce même poste (`planification.py`, `route_admissible.py`, `pnj._marcher` : l'eau) ; 56 sur
l'autre poste (comptes : `biens.py`, `echanges.py` côté `reclamer`, `paroles.py`, `mj.py`). Ce lot touche
`donjon/pnj_propositions.py` et, s'il le faut, `relations.chance_proposition` et la retenue des refus
(`deliberation.retenir_refus`, `tient`) ; pas `planification.py`.

Lis `AGENTS.md`, `docs/etat-dev.md` (**« Vérification d'intégration 5c2ce81 », défauts (4), (5) et (6)** ; entrée
`codex-proposer-recours` lot 45 ; `refus-retenus`), `docs/plan-relations.md` § 7.1 et 7.2 (décision « faute de
mieux »), le rapport `docs/taches/rapport-codex-45-proposer-recours.md`, puis `donjon/pnj_propositions.py`
(`_contreparties`, `_entrees`, `_tient`, `recours`, `executer`), `donjon/echanges.py` (`evaluer_proposition`,
`proposer`), `donjon/deliberation.py` (`retenir_refus`, `tient`, `moyens_crus`). Bruts de l'audit :
`C:\Users\msics\donjon\artifacts\verif-integ-5c2ce81\` (`extraits.txt`, `audit-12h\`).

## Le constat (audit 12 h de l'intégration 5c2ce81, 32 nuits)
- **Offres redites sans fait nouveau** : crue 11, Brune propose six fois à Gorm « la torche contre une part des vivres »
  (367, 368, 374, 386, 461, 593), refusée chaque fois par méfiance (`demande_en_boucle`) ; offres identiques reprises
  en moins d'une heure, sur 8 nuits : Relais 6, mine 14, auberge 16, crue 14 ; 18 offres en pièces répètent au même
  prix ou moins un achat refusé moins de deux minutes avant. Le lot 45 promettait « pas de réessai par le simple délai ».
- **Contreparties absurdes** : Bram offre « la clé de la paie » (ce qu'il garde) contre une part de vivres (mine 42,
  637) ; Josse « le passe du contremaître » ; Odon « l'outil de serrurier contre la bourse de la paie » (toute la paie
  contre un outil). Acceptées : 8/55, 11/186, 29/176, 4/79.
- **Tâche acceptée puis abandonnée dans la minute** : crue 7, 351-353, Ilse accepte à 5 pièces la tâche de Gorm et
  la chronique note `engagement_abandonne` la même minute.

## L'invariant
**Le proposant juge sa propre offre par les règles communes qu'il appliquerait à une demande qu'on lui ferait** : il
n'offre pas ce qu'il garde (`garde`), ce qui lui est nécessaire (`necessaire`), ni ce dont la valeur propre pour lui
dépasse ce qu'il espère obtenir (une seule fonction de valeur, celle d'`evaluer_proposition`) ; **et une offre refusée
se retient comme un refus**, par sa cause, et ne se redit qu'avec un moyen cru nouveau ou une offre plus forte (la
règle de `refus-retenus`, sauvegardée, la même pour un achat). Une tâche acceptée ne s'abandonne pas sans fait
nouveau : trouve pourquoi Ilse l'abandonne la même minute (devis d'acceptation et devis d'exécution différents ?) et
corrige la règle commune. Pas de liste d'objets ni de personnages.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : Brune et Gorm à la crue (une offre refusée ne revient qu'avec un fait
  nouveau) ; Bram ne propose jamais la clé de ce qu'il garde ; Odon n'offre pas plus qu'il n'obtient ; une offre
  sensée toujours faite et acceptée (le cas du lot 45) ; la tâche d'Ilse tenue ou refusée, jamais acceptée puis lâchée
  dans la minute.
- Banc rapide (`tools/comparer_bancs.py --reference c592d68`, 4 h, 4 graines, quatre scénarios) puis l'audit 12 h des
  seules nuits citées (crue 11, mine 42, mine 1985, crue 7), branche seule : offres, acceptées, redites, vols.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-relations.md` § 7.2, `docs/etat-dev.md` (« Branche
`codex-offre-sensee`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-57-offre-sensee.md`.
