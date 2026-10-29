# Lot 279 — les six coups de la crue 2024 : diagnostic

29 octobre 2026, branche `codex-coups-crue-2024`, base intégration `792816c`.
Aucun fichier de `donjon/`, `tools/`, `tests/` ni scénario modifié ; aucun Luna,
suite complète ni banc comparatif. Trois rejeux détachés, **un processus à la fois,
priorité réduite** : `792816c` (nuit actuelle), `0bad227` (code de l'alerte 274) et
`c870c8b` (`main`). Scénario `crue`, graine 2024, 12 h, départ tiré, joueur passif
dans la chambre de la cloche. Bruts et scripts :
`C:/Users/msics/donjon/artifacts/coups-279/`.

## Reproduction

- `0bad227` : **15 frappes, 6 coups portés**, 16 PV perdus ; Brune passe de 16 à
  0 PV, inconsciente de `357710` à `360087` (3,96 min), ranimée à 1 PV. Aucun mort,
  aucun assomment réussi. Chronique de 698 lignes, empreintes, récit et souvenirs
  **identiques à l'archive 274** ; seules les clés de la sonde 219 manquent aux
  mesures du rejeu.
- `792816c` : **aucun coup**. Premier écart avec `0bad227` à l'instant `3314`
  (min 5) : Aubin appelle Brune et lui donne une part des vivres (`service_rendu`,
  `vivres_1`), que `0bad227` ne fait pas ; sa faim reste à **45** à 595 au lieu de
  **95**. Le rapport 266 documente le même maintien de la raison de nourrir Brune
  (Relais 2024) ; le lot n'est pas isolé par bissection et cette non-reproduction
  n'est pas une correction de `0bad227`.
- `c870c8b` : aucun coup, 796 lignes identiques à son archive.

## Qui frappe qui

Tous les instants sont dans la minute 596 (`t` en dixièmes de seconde).

| `t` | auteur → cible | geste | but (motif) | issue | PV cible |
|---:|---|---|---|---|---:|
| 357620 | brune → aubin | assommer, pied-de-biche | manger `vivres_1` (faim) | manque | 18 |
| 357620 | marchand → brune | frapper, bûches du guet | protéger Aubin (devoir) | manque | 16 |
| 357635 | marchand → brune | frapper | protéger Aubin (devoir) | porte 3 | 16→13 |
| 357635 | brune → marchand | frapper, pied-de-biche | riposter (sécurité) | esquivé | 20 |
| 357635 | aubin → brune | frapper, vivres | riposter (sécurité) | manque | 13 |
| 357650 | marchand → brune | frapper | protéger Aubin | porte 3 | 13→10 |
| 357650 | aubin → brune | frapper | riposter | manque | 10 |
| 357665 | marchand → brune | frapper | protéger Aubin | porte 5 (20 nat.) | 10→5 |
| 357665 | aubin → brune | frapper | riposter | manque | 5 |
| 357680 | marchand → brune | frapper | protéger Aubin | manque | 5 |
| 357680 | aubin → brune | frapper | riposter | manque | 5 |
| 357695 | marchand → brune | frapper | protéger Aubin | porte 3 | 5→2 |
| 357695 | aubin → brune | frapper | riposter | porte 1 | 2→1 |
| 357710 | marchand → brune | frapper | protéger Aubin | manque | 1 |
| 357710 | aubin → brune | frapper | riposter | porte 1 | **0, inconscience** |

Gorm protège **Aubin** ; le champ `qui` enregistré vaut `brune` (défaut ci-dessous).
La sonde 219 de l'archive ne retient aucun retour non justifié et ne certifie aucun
suspect ; ses dérives `357600` (Brune) et `357620` (Gorm) restent
`suspect_certifie=false`.

## Chaque coup est justifié par les contrats existants

- **Brune** décide à 596,0 un plan `manger vivres_1` : `dans_le_dos`, `assommer`
  Aubin au pied-de-biche, prendre, manger. À l'exécution sa faim vaut **95,088**,
  au seuil `DESESPOIR = 95` : l'embuscade est permise malgré Gorm témoin
  (`embuscade_possible`), et le prix de la faute (**29,68 ≤ ENJEU 60**) reste
  admissible. C'est le **seul coup non défensif** de la nuit ; il manque.
- **Gorm** voit l'assomment de Brune contre Aubin (`violence`, source `vu`,
  minute 596). `protection` renvoie `(aubin, antichambre, [brune])` : il protège
  Aubin. Ses **7 coups** sont des interventions ; chacun est revalidé par
  `pnj._executer_effet` (cible dans `protection(...)[2]`, consciente, au contact)
  puis par `combat.frapper` (arme tenue, contact). Douceur 100, défense : prix 0.
- **Aubin** a vu l'assomment contre lui et le coup de Brune contre Gorm (source
  `vu`, minute 596) ; sa sécurité monte à 100, ce qui rend sa défense payable.
  Ses **6 ripostes** visent une cible consciente et au contact.
- **Brune** voit le coup de Gorm (source `vu`) et **riposte** une fois, sans
  toucher ; cible consciente et au contact.
- Le dernier coup (Aubin, `357710`) fait passer Brune de 1 à 0 PV et déclenche
  `endormir` au même instant. `constater_fin` ferme alors les croyances de
  violence (`clos: true`) : à 597, `dangers=[]` pour Gorm et Aubin, et **aucun
  coup ne suit l'inconscience**. Les six souvenirs `secours` de Brune sont tous
  `examine: true` ; Gorm passe à `ranimer Brune` (réveil à `360087`), Aubin lui
  donne une part au même moment. Ni riposte en boucle après la neutralisation,
  ni secours non acquitté, ni cible non revalidée, ni mort.

## Le défaut établi : le but nomme l'agresseur

`planification.reagir` rend `{"type": "proteger", "qui": ennemis[0]}` : ici
`qui = brune`, alors que Gorm protège **Aubin** et que le plan frappe Brune.
`recit_pnj.but_en_mots` affiche donc « protéger Brune » et
`paroles.engagements_enregistres` fournit au MJ « intention en cours : protéger
Brune ». Le joueur passif de cette nuit ne l'a pas vu, mais une question à Gorm
pendant ou après l'échauffourée produirait une affirmation incompatible avec
l'état. Le lot 222 avait déjà relevé que `but.qui` désigne l'adversaire ; le
défaut est toujours présent dans `792816c`.

**Petit lot proposé, sans correction ici** : invariant « un but de protection
nomme le protégé ; l'agresseur reste la cible du plan ; aucun récit, relevé ou
texte fourni au MJ ne présente l'agresseur comme le protégé ». À instruire :
`planification.reagir` (champ du but), `recit_pnj.but_en_mots`,
`paroles.engagements_enregistres`, le relevé d'`audit_nuits` et les tests qui
lisent ce libellé. Aucune branche propre à la crue, à Brune ou à un objet.

## Premier écart entre `c870c8b` et `0bad227`

Index 38 de la chronique, instant `978` (min 1) : `c870c8b` n'a que « Gorm se
retourne au bruit » à `984` ; `0bad227` ajoute « Gorm : agenda `evacuer_crue`
actif (mandataire estime) » à `978`. Ce texte est introduit par le **lot 260**,
commit `c5d7301` (`agendas.py:699`), absent de `c870c8b`. Les trajectoires
divergent ensuite ; la chronique seule ne permet pas de désigner un lot causal
de l'échauffourée, et aucune bissection n'a été faite.

## Captures

`0bad227` : cinq captures (`595-avant`, `596-avant-coup`, `597-apres`, `600`,
`605`). Pour chacune, `monde`, `rendu` et `scene` sont **identiques après
`sauver`/`charger`**, et la capture ne mute pas le monde. À 600, Brune a 0 PV et
est inconsciente depuis `357710` ; à 605, elle a 1 PV, est consciente et se
trouve dans la chambre de la cloche. `792816c` et `c870c8b` ont quatre captures
(595, 597, 600, 605), mêmes contrôles, zéro coup.

## Limites

Aucune garantie universelle : la détection des contradictions mécaniques reste
en partie sémantique, et ce diagnostic porte sur une nuit et un code. `792816c`
ne reproduit pas les coups ; cela ne corrige ni ne certifie `0bad227`, et la
cause de cette non-reproduction n'est pas isolée (piste 266, non certifiée).
Le défaut du libellé est un défaut de restitution et d'audit, pas un défaut du
coup lui-même. Ni banc de 8 à 12 h, ni audit de nuits, ni `VERIFIER`, ni Luna,
ni suite complète.
