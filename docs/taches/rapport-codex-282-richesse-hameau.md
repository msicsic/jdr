# Lot 282 — richesse et attente du hameau entre `c870c8b` et `0bad227`

29 octobre 2026, branche `codex-richesse-hameau`, base intégration `3470a92`. **Diagnostic seul** :
aucun fichier de `donjon/`, `tools/`, `tests/` ni scénario modifié, pas de Luna, pas de suite complète,
pas de banc comparatif. Archives 274 relues d'abord ; quatre nuits rejouées détachées, **un processus à
la fois, priorité réduite** (`0bad227` et `c870c8b`, graines 1985 et 2024, 12 h, départ tiré, joueur
passif), **688,9 s**. Identité aux archives sur les quatre nuits : chronique, mesures, récit, souvenirs,
empreintes, relevés et plantage égaux. Bruts, scripts et captures :
`C:/Users/msics/donjon/artifacts/richesse-282/`.

## Mesures par graine (`c870c8b` → `0bad227`)

| Graine | Attente | Sans recours | Noir | Eau | Propositions / acceptées | S / F / D |
|---|---:|---:|---:|---:|---:|---:|
| 1985 | 840 → 1 010 | 15 → 0 | 80 → 290 | 30 → 20 | 23/5 → 15/1 | 84/9/3,83 → 62/9/3,83 |
| 7 | 1 155 → 1 165 | 0 → 0 | 110 → 20 | 20 → 20 | 15/3 → 6/2 | 65/9/3,67 → 58/9/3,33 |
| 42 | 525 → 485 | 0 → 0 | 90 → 195 | 15 → 15 | 14/1 → 16/1 | 45/9/3,00 → 52/9/3,33 |
| 2024 | 1 205 → 1 590 | 0 → 0 | 35 → 25 | 15 → 0 | 16/3 → 8/5 | 64/8/3,33 → 53/7/3,17 |
| Moyenne | **931 → 1 062** | 3,75 → 0 | **79 → 133** | 20 → 14 | **17/3 → 11,25/2,25** | **64,5/8,75/3,46 → 56,25/8,5/3,42** |

Familles `cats` (lot 183) : 1985 appels 10→7, demandes 43→32, offres 22→15, promesse 1→0, travail payé
4→8 ; 7 offres 14→4, demandes 58→43 ; 42 appels 4→7, demandes 21→25 ; 2024 offres 13→6, appels 5→2,
**interposition 3→0** (famille perdue). Signatures perdues/gagnées : **47/25, 33/26, 3/10, 41/30**.

## Attentes : qui, quel besoin, quel intervalle

Relevés toutes les 5 min (`inactivité` = `attente`), sommes égales aux mesures. Sur les deux nuits
instrumentées (1985, 2024), **aucun refus retenu** (`renoncements` vide) et aucun « renonce » : tous les
recours rendent **« rien »**.

- **1985 (+170)** : Gorm/devoir **0 → 395** (310 devoir, 45 devoir+chaleur, 40 devoir+biens), Aubin/chaleur
  380 → 530 ; en baisse Ilse/chaleur 160 → 15, Maël/chaleur 245 → 70, Brune et Sève/faim 55 → 0.
- **7 (+10)** : Gorm/devoir 0 → 440, Brune/chaleur 105 → 170 ; compensé par Sève/faim 330 → 130,
  Brune/faim 145 → 0, Aubin/chaleur 110 → 0.
- **42 (−40)** : Sève/faim 380 → 375, Brune/faim 125 → 90 ; pas de stagnation de Gorm.
- **2024 (+385)** : Maël/chaleur 0 → 365 (360-720), Brune/chaleur 0 → 360 (355-720), Sève/faim 5 → 335
  (390-720), Aubin/chaleur 260 → 300 (+80 chaleur+faim) ; en baisse Gorm/devoir 380 → 0 (5 avec biens),
  Brune/faim 315 → 5.

## Juste ou défaut

- **Le premier écart substantiel des quatre nuits tombe à la minute 1-2 sur le même point** : l'offre que
  Brune choisit. `c870c8b`, 1985 : « Brune propose à Ilse la promesse que la torche soit allumée contre
  1 pièce (accepte) » ; `0bad227` : « … la trousse de crochets contre 8 pièces (pauvre) ». En 2024,
  `c870c8b` ajoute à la minute 2 la même promesse à Aubin (marche) et à Gorm (mefiance) ; `0bad227` non.
  C'est l'effet **décrit et accepté au lot 228** (`etat-dev` : « Brune préfère désormais la vente
  compensée de ses crochets (autre choix, service non interdit) », `8567c47`/`e8feb8f`). En 7 et 42, le
  premier écart n'est qu'un ordre d'événements identiques ; même signature d'offre plus tard, sans lot
  causal unique.
- **1985 : juste.** Le service payé de la torche manque (228), et le devoir de Gorm n'a plus aucun plan :
  catalogue vérifié aux captures 95 et 360 : `interposition` → `None` (aucune approche perçue à deux cases
  avec un méfiant ; il s'interpose à 2, 5, 536, 636), bruit/`voir` → `None`, ronde de la crypte et
  brasero → `None` car **crypte, beffroi et échoppe sont crues menacées par l'eau** dès 95 (le brasero
  n'y est ni allumé ni alimenté : « un feu là où il attend l'eau »). Les 395 min sont donc une contrainte
  réelle, pas un recours refusé ; l'essentiel des 23 propositions de la base (ses demandes et offres de
  413 à 653) disparaît avec elle.
- **7 : juste par la mesure et les signatures, catalogue non instrumenté.** Même stagnation de Gorm
  (0 → 440), compensée : Maël obtient une part à 253, Gorm sert Aubin à 255 et Sève à 521 ; Sève/faim
  330 → 130, Brune et Aubin ne pressent plus. S −7 = offres/demandes en moins, aucune interaction refusée.
- **42 : juste.** Aucune stagnation ; S +7 (appels 4 → 7), attente −40. L'attente de Sève est inchangée
  (380 → 375, faim) et elle passe plus de temps dans le noir du beffroi (90 → 195) ; aucun écart d'attente
  à instruire, et la nuit n'a pas été rejouée (aucun besoin).
- **2024 : juste, mais la chaîne est matérielle et vaut d'être connue.** 228 fait vendre les crochets ;
  Aubin promet à Gorm d'allumer la torche contre une part de vivres (82, accepté), **la prend et l'allume**.
  La torche est son propre réservoir et **ne se recharge pas** (`perception.brule`) : 60 min de réserve,
  vide à ~142. Plus aucune flamme portable : briquet et lanterne sont au joueur (inconnus de tous), le fanal
  est fixe (`mobile=False`). Les deux foyers restent éteints (poêle 0, brasero 0) malgré le bois au poêle
  (`bois_guet`, 4 charges) : `_plan_froid` → `None` pour Maël, Brune, Aubin. La réserve vidée à 195 (deux
  parts à Maël) fait croire à une disparition ; Gorm garde (biens 100) et ne sert plus. **Contrainte réelle**,
  aucun recours refusé. Le seul moyen admissible qui l'aurait rompue — emporter une flamme du fanal allumé
  (brandon) — n'existe pas dans le modèle ; le lot 277 (non fusionné) ne couvre que « demander à qui porte
  une flamme », or plus personne n'en porte après 142.

**Aucun défaut du moteur n'est établi** : aucune contradiction mécanique relevée (joueur passif, aucune
parole de MJ à contrôler), aucun recours admissible refusé, aucun renoncement retenu et aucune répétition
sans entrée nouvelle ajoutée (1 → 1 sur 1985). **Aucun petit lot de correction n'est proposé.** Deux points à
instruire seulement : ne pas rouvrir 277 pour la nuit 2024 (il ne la couvre pas) ; si l'on veut la
robustesse, le manque général est « emporter une flamme d'un foyer fixe allumé », capacité nouvelle et non
contradiction d'état — à briefer séparément.

## Captures et limites

Dix captures par nuit (`5, 95, 360, 371, 386, 404, 450, 495, 655, 720`), **40 recharges** : monde, rendu et
scène identiques après `sauver`/`charger`, la capture ne mute pas le monde. Sonde 219 : aucun suspect
certifié ; « entrée nouvelle à expliquer » 42 → 12 sur les quatre nuits.

S/F/D mesure des signatures, pas des épisodes causaux (même texte fusionné, services sans transition de
bande sous-comptés) ; l'attribution des attentes vient du relevé de 5 min. Le rejeu porte sur les deux
commits comparés, pas sur `3470a92` (la nuit 1985 est identique à l'archive au `792816c`, lot 278). Aucune
garantie universelle : la détection des contradictions mécaniques reste en partie sémantique, et une
trajectoire admissible peut appauvrir la nuit sans qu'un contrat soit violé.
