# Lot 291 — G2 : les refus publics appartiennent au moteur

2026-10-29. Branche `codex-g2-refus-moteur`, base intégration `931b22b`
(brief présent), code `031e664`. **Lot terminé, non fusionné.**

`MJ._echanger_prepare` garde la correction bornée sur copie et `retour_refus`
avec `attendu`. Sans action admise, `reponse_du_moteur` affiche les messages
publics exacts, distincts et ordonnés, sans audit. Forme persistante : demande
de précision moteur. Appel final d'explication, `ExplicationCedee` et
`_sans_relance` supprimés. Contre-revue, fidélité de parole, qualifications
et audits des autres voies conservés ; aucune mécanique PNJ modifiée,
aucune exception propre aux exemples.

**209 tests distincts / 16 fichiers verts**, zéro échec, erreur ou ignoré ;
377,879 s. Sept nouveaux tests console : portée (poutre et crochets),
passage trop bas (Relais et auberge), formes persistantes, deux causes,
dialogue/avis écartés. Texte sauvegardé, monde et rendu après recharge
vérifiés. Attentes adaptées uniquement pour l'explication libre ou son
coût : artisanat, défi, improvisation, contrats internes, narration.
Ni suite complète ni banc PNJ supplémentaire.

**Luna : une passe, quatre scripts, sans rejeu**, `integ=931b22b` et `lot=.`
sur `031e664` ; copies, coffre principal, un travailleur réduit. Références
absentes jouées une fois, aucun cache réutilisé. **Six tours refusés** : texte égal au
message public, aucun `attendu`, **0 appel final d'explication et 0 audit
après le refus public, dans chaque tour** :

| Script / tour | Message public lu | Appels totaux / secondes |
|---|---|---:|
| relais 21 | Approche-toi de la poutre effondrée : il faut être juste à côté pour agir. | 1 / 1,79 |
| relais 22 | Approche-toi de la poutre effondrée : il faut être juste à côté pour agir. | 1 / 1,70 |
| relais 23 | Tu ne vois rien de tel ici. | 3 / 6,55 |
| sous-obstacle-trop-bas 1 | Le dégagement est trop bas pour passer en rampant. | 2 / 6,85 |
| atelier 3 | Approche-toi de la perche de bois 1 : il faut être juste à côté pour agir. | 1 / 2,36 |
| atelier 14 | Approche-toi du mur de l'atelier : il faut être juste à côté pour agir. | 4 / 10,13 |

Corrections après refus aux tours relais 23 et trop-bas 1 ; l'audit de
l'avis atelier 14 précède le refus public. Sept occurrences publiques,
six messages affichés ; deux `REEXAMEN` non affichés. Référence :
**3 générations finales d'explication + 3 audits**, atelier 13 ; dialogue
de correction et audit aussi au relais 23, désormais remplacés par le moteur.

Global référence → lot : **60 → 57 appels**, **2,86 → 2,59 appels/tour MJ**,
**8,84 → 5,75 s/tour**, refus **12 → 9**, tours refusés **7 → 6**, replis
**2 → 0**, relances **3 → 3**. Limite : un délai réseau au premier tour
`sous-obstacle-relais` de référence (47,96 s) empêche sa tentative suivante ;
21 tours MJ contre 22. Hors ce script : 2,95 → 2,65 appels/tour,
6,88 → 5,93 s/tour ; une passe ne démontre aucun gain causal.
**Surcoûts observés** : atelier 10, outils, **2 → 4 appels**, **4,72 → 9,62 s**,
une relance de perception ; atelier 14, saut, **1 → 4**, **3,07 → 10,13 s**,
un refus de forme et une relance de justification supplémentaires avant
la portée. Atelier 13 perd un repli et trois refus ; relais 20 perd une
relance. Aucune régression de l'invariant observée ; les autres audits
restent hors portage.

L'analyse initiale échouait sur l'incident **de référence** ; son compteur
mélangeait générations et audits (6 au lieu de 3 + 3). Script seul corrigé,
**code 0, invariant vrai 6/6** ; incident conservé. Bruts et empreintes dans
`C:/Users/msics/donjon/artifacts/g2-291/` : huit parties et fils, banc complet,
tests, analyse corrigée, `mesures-luna.json`, `manifest-bruts.json`,
`fin-analyse.json`. `fin-luna.json` garde l'échec initial pour traçabilité.
