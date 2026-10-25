# Lot 80 — Dire son avis sur la menace d'un lieu

Branche `codex-avis-menace`, non fusionnée ; base **882907c**, brief **5fd85a1**,
code signé SSH **a2bb274**. Aucun appel à Luna, changement de scénario ou de `main`.

**Invariant.** `social.nouvelles` → `bavarder` → `recevoir` transmet l'avis de menace
à qui le locuteur croit dans ce lieu ou attendu à un rendez-vous convenu, si altruisme
+ empathie + affection ≥ 100. La confiance envers l'auditeur n'est pas nécessaire pour
le prévenir. Destinataire et témoins pèsent source × conviction (§ 7.3), sans jet ;
l'égalité conserve la croyance acquise. Les relais gardent la date de preuve et perdent
en conviction. Le registre du lot 64 suit menace et destinataire, sans répétition pour
une nouvelle date ou conviction.

**Raccord autorisé dans `eau.py`.** La croyance reçue `prevision` reste distincte des
mesures. `attendue` départage estimation propre et avis ; `menacee` lui délègue. Une
estimation propre étayée plus récente dément durablement l'avis, sans redater le repère
de vitesse. `attendue(projection=True)` fournit aussi les coefficients aux routes.
Raccord minimal dans `Vue`/`route_admissible`, coefficients dans `_entrees` ; algorithmes
de recherche et règles de choix des buts inchangés.

**Preuves.** Crue 500, tirage inchangé : Aubin observe les vannes à 140 et 155 min,
prévient Ilse et Gorm ; Ilse croit et gagne la galerie, Gorm sans confiance doute.
Porte ouverte et abri connu pour isoler l'information. Autre lieu/locuteur/auditeur,
constat contraire, égalité, preuve propre récente, souci, destination, non-répétition,
parole restituée depuis la sauvegarde. Même laps découpé : état complet, avis et rendu
après recharge identiques ; les résumés visuels transitoires restent propres aux tranches.
Suite complète unique : **1 903 tests, 16 ignorés**, 193 fichiers, trois processus à
priorité réduite, **1 477,7 s** ; seul échec de la nouvelle scène d'écoute sans mode
spatial. Scène corrigée ; après resserrements finaux, **18 tests verts en 31,5 s** :
huit avis et dix tests inchangés des lots 41/58. Bilan consolidé vert, sans seconde suite.

**Mesures.** Empreintes **2 h, crue/Relais × quatre graines, sans avis : identiques**
(état, chronique, mesures communes ; deux compteurs nouveaux vérifiés nuls puis retirés).
Sonde hors jeu `artifacts/80-sans-avis.py`, références calculées une fois et mises en cache.
Rapide **4 h, mêmes scénarios/graines** : états et chroniques identiques à la base,
**0 avis / 0 adoption**, aucun plantage ou usurpation ; eau crue **133,75 → 133,75
min·PNJ**, `eau_longue` **1 → 1**, `voir_alterne` **2 → 2** ; Relais `fige_presse` **3 → 3**.
Aucune boucle nouvelle relevée.
Audits 12 h, branche seule : aucun plantage/usurpation, zéro avis/adoption.

| Graine | Eau (min·PNJ) | `eau_longue` | Lieux à 12 h |
| --- | ---: | ---: | --- |
| 500 | 1 095 | 4 | Gorm refuge ; Brune galerie ; Ilse conduite ; Aubin vannes |
| 2024 | 275 | 1 | Les quatre au refuge |

L'alerte de répétition d'Ilse porte sept hauteurs différentes (32/50/73/67/55/43/29 cm).
Contrôle `VERIFIER` et `spatial.VERIFICATION=1`, crue 42, 2 h : **aucun écart, borne
atteinte ou plantage**, 586,7 s.

**Limites.** Menace d'eau seulement, sans dispute ni lecture des plans privés. L'avis
porte sur le lieu annoncé ; il peut être faux près du pic caché de la crue. Un sol sec
ne réfute pas à lui seul une prévision future. `changements_d_avis` compte les adoptions
par parole. Les nuits mesurées n'émettent aucun avis : la preuve d'émission reste celle
des parcours ciblés. Créneau dépassé par le travail et les vérifications prescrites.
Traces dans `artifacts/80-*`.
