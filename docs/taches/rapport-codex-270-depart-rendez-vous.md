# Lot 270 — départs juste après « Ici, viens ! » dans la crue

28 octobre 2026, PC fixe. **Branche `codex-depart-rendez-vous`, non fusionnée**,
base d’intégration `4d2881f` ; archives de la vérification 241 sur `c870c8b`.
Diagnostic seul ; **aucun code du jeu modifié**. Rejeu instrumenté en mémoire,
une nuit à la fois, priorité réduite. Ni Luna, suite complète, ni banc comparatif.

**Méthode.** Repérage textuel identique à `suivis241.py` sur les huit graines
`audit-12h` et sur `verifier-8h` : **15 lignes, 11 cas distincts**. Chaque
échange est relu dans la chronique archivée (Invitation, `J'arrive !`, annonce
de rupture, ouïe, épisode `recit`). Les cas sont ensuite rejoués sur
l’intégration actuelle avec des sondes en mémoire (`appel.dire`,
`appel.rompre_attente`, `deliberation._attendre_qui_vient`), qui donnent le
palier réel, le partenaire et l’audition. Chaque nuit est rejouée avec les
paramètres de l’audit 241 : `crue`, départ `tire`, joueur en `chambre_cloche`,
12 h. L’intégration actuelle ne reproduit
plus la graine 42 (empreintes différentes dès 5 min) ; ses quatre cas, dont
trois à 281–282, sont rejoués sur `c870c8b` dans un worktree détaché, avec les cinq
empreintes 5/60/120/240/480 **identiques à l’archive**. La graine 11, elle, est
identique à partir de 60 min et ses départs sont reproduits.

| # | Nuit | Départ (min.) | Classe et cause | Annonce | Verdict |
|---|---|---|---|---|---|
| 1 | audit/11 | Ilse→Aubin 1→2, Galerie de ronde | palier > : sûreté/évacuation (archive 0/5 ; rejeu 4) | oui, entendue | justifié |
| 2 | audit/1985 | Aubin→Ilse 1→1, Salle des vannes | **venue** : `J'arrive !` à 1, puis `accourir` | — | pas une rupture |
| 3 | audit/1985 | Ilse→Aubin 1→2, Galerie de ronde | palier > : parole due 5 (`engagement`) | oui, entendue | justifié |
| 4 | audit/2024 | Ilse→Aubin 1→2, Galerie de ronde | palier > : parole due 5 (`engagement`) | oui, entendue | justifié |
| 5 | audit/2024 | Aubin→Ilse 1→2, Conduite basse | **venue** : `J'arrive !` à 1, puis `accourir` | — | pas une rupture |
| 6 | audit/42 | Aubin→Ilse 1→2, Palier des vannes | **venue** : `J'arrive !` à 1, puis `accourir` | — | pas une rupture |
| 7 | audit/42 | Ilse→Aubin 281→281, Palier des vannes | palier > : besoin pressant 4 (`faim`/enquête) | oui, entendue par Aubin | justifié |
| 8 | audit/42 | Brune→Ilse 281→281, Salle des vannes | palier > : eau 0 (`abri`) | oui, entendue par Ilse | justifié |
| 9 | audit/42 | Ilse→Brune 281→282, Galerie de ronde | **clos** : attente d’Ilse rompue à 281 ; aucune attente ouverte à 282 | — | écarté : clos |
| 10 | audit/7 | Aubin→Ilse 1→2, Palier des vannes | **venue** : `J'arrive !` à 1, puis `accourir` | — | pas une rupture |
| 11 | audit/99 | Ilse→Aubin 1→2, Galerie de ronde | palier > : eau 0 (`sûreté` ; rejeu 4) | oui, entendue | justifié |
| 12 | vérif/42 | Aubin→Ilse 1→2, Palier des vannes | doublon de 6 | — | écarté : doublon |
| 13 | vérif/42 | Ilse→Aubin 281→281, Palier des vannes | doublon de 7 | oui, entendue | écarté : doublon |
| 14 | vérif/42 | Brune→Ilse 281→281, Salle des vannes | doublon de 8 | oui, entendue | écarté : doublon |
| 15 | vérif/42 | Ilse→Brune 281→282, Galerie de ronde | doublon de 9 | — | écarté : doublon |

**Doublons.** `verifier-8h/crue_42` rejoue la même nuit que `audit-12h/crue_42` :
les 665 lignes de chronique jusqu’à 480 min et les cinq empreintes 5/60/120/240/480
sont identiques ; seule l’empreinte `issue` diffère. Les quatre lignes 12–15
répètent donc 6–9. **15 lignes = 11 cas distincts** : 4 venues, 1 clôture,
6 ruptures.

**Captures avant départ, sauvegardées puis rechargées** (`Monde.sauver` /
`Monde.charger`) : `avant_depart_42_ilse_281.json` (`105ac6d077d4`) et
`avant_depart_42_brune_281.json` (`bd21490ad3d1`) sur `c870c8b` ; monde
identique, empreinte identique, rendu du joueur identique. Idem pour
`avant_depart_11_ilse_2.json` (`b367c49ce0ec`) et
`avant_depart_1985_ilse_2.json` (`cae867545099`) sur l’intégration actuelle.
Les deux captures de 281 précèdent le départ avec l’attente encore ouverte
(`rejoint` d’Ilse pour Aubin, `jusqu_a` 285 ; de Brune pour Ilse, `jusqu_a` 284).

**Verdict : départs justifiés, aucun défaut du moteur.** Les 15 lignes ne sont
pas 15 ruptures. Quatre cas distincts sont la **venue promise** (`J'arrive !`
puis départ vers l’appelant) : le rendez-vous s’exécute, il ne se rompt pas.
Un cas survient après **clôture** : à 282, Ilse n’a plus d’attente ouverte, sa
propre rupture de 281 et celle de Brune ont déjà été annoncées et entendues.
Les six ruptures distinctes restantes ont toutes un **palier strictement
supérieur** à l’attente (8) : eau 0, besoin pressant 4, parole due 5 ; chacune
est annoncée par `appel.rompre_attente` et **entendue par le partenaire**
(`entendu_partenaire=true`, champ `rejoint`/`rejoindre` remis à `None`). Aucun
départ sans cause, aucune échéance dépassée, aucune rupture non annoncée.

**Le comptage textuel de la 241 doit les écarter.** Il compte un départ dans la
minute d’un « Ici, viens ! », pas une attente encore ouverte ni une rupture : il
garde un `pending` par PNJ, sans l’état réel de l’attente (`rejoint.qui`,
`vient`, échéance), sans le `J'arrive !` du même PNJ, sans la rupture entendue
de l’autre, et sans déduplication des nuits rejouées dans deux groupes. La hausse **10 → 15** n’est
donc pas cinq violations nouvelles : elle ajoute deux cas du cluster 42
(×2 groupes), trois ruptures d’Ilse à 2 min, et perd deux cas `marchand` de
`4306c14`.
Si le superviseur veut un compteur fiable, un petit lot d’**outillage** suffit :
suivre le partenaire effectif, clore sur le `J'arrive !` du même PNJ, sur la
rupture entendue et sur `appel.retrouves`, puis compter par nuit distincte.
Aucun lot de correction du jeu n’est proposé.

**Limites.** L’archive ne stocke ni le palier numérique ni le destinataire d’une
rupture : pour les quatre ruptures d’Ilse à 2 min, le palier exact vient du
rejeu de l’intégration actuelle (4 ou 5), l’archive n’en donnant que l’épisode
(`securite`/`engagement`). Sur les nuits qu’il reproduit, le rejeu actuel
ajoute un cas de même famille non compté par la 241 (graine 7, Aubin à 254,
`J'arrive !`) ; il ne crée pas de rupture. Les captures prouvent l’état **avant** départ, pas l’état après ;
l’après est couvert par les sondes (rupture annoncée, partenaire clos) et par
l’identité exacte du rejeu `c870c8b` de la graine 42.

Bruts : `C:/Users/msics/donjon/artifacts/rendez-vous-270/` (`rejeu.json`,
`rejeu_c870c8b.json`, `cas_archives.json`, `classement_archives.json`,
`captures/`, `captures_c870c8b/`, scripts). Le worktree détaché
`C:/Users/msics/donjon/.worktrees/rendez-vous-270-ref` a servi au seul rejeu de
`c870c8b` et est retiré après. Aucun calcul actif.
