# Lot 268 — réveils de l’agenda de Brune

28 octobre 2026, laptop. **Branche `codex-agenda-brune`, non fusionnée**,
base d’intégration `a6ecefd` (moteur de `1355f7a`). Diagnostic seul ; aucun
code du jeu modifié. Deux nuits successives **4 h, hameau 2024, départ tiré,
joueur passif en `chambre_cloche`**, un processus réduit à la fois.
Ni Luna, suite complète, ni banc comparatif.

**L’alerte huit/neuf n’est plus reproduite sur l’intégration actuelle.**
La chronique contient **4 lignes actif / 3 sommeil**, mais seulement **deux
réveils** : la naissance puis le changement de raison `dette_situation` →
`plan admissible` produisent deux lignes actif sans sommeil intermédiaire.
Sur la base historique demandée **`881db69` détachée**, on retrouve
**8 lignes actif / 7 sommeil**, soit **six réveils**. Cela retrouve la famille
de répétitions ancienne, pas les neuf/neuf du moteur corrigé du 218.
L’alerte est donc absente au plus tard avec le moteur de `1355f7a`, encore
présente sous une forme proche sur `881db69` ; **premier commit de disparition
et causalité non établis**. Arrêt après ces deux nuits, conformément au brief.

**Contrat observé.** `a1` est un agenda **obtenir 20 pièces**, né de la dette
personnelle ; budget `agendas.poids`, palier `BESOIN_PRESSANT`. Chaque sommeil
ci-dessous porte **« sans plan admissible au cout »**. Les essais sont filtrés
par `essayables` / `_croyances`, et `planifier` n’active qu’après un recours
retourné par `argent_projet.obtenir`. Les dates de regard seules sont exclues
de l’empreinte. Temps ci-dessous : **dixièmes de seconde depuis le départ**.

| Version | Sommeil → réveil → sommeil | Entrée observée et recours au réveil |
|---|---|---|
| Actuelle | 374 → 591 → 747 | Crochets pris à 571, possession nouvelle ; vente proposée à Ilse, 8 pièces, acceptée à 647. |
| Actuelle | 747 → 929 → 1095 | Pied-de-biche pris à 822, Gorm désormais cru en antichambre ; trajet puis offre d’allumer sa torche pour 1 pièce, refusée à 990. |
| 881db69 | 444 → 495 → 600 | Gorm cru passé en antichambre, lumière de l’échoppe changée, outils découverts ; trajet et offre d’allumage à Gorm. |
| 881db69 | 600 → 738 → 934 | Lumière 1 → 2, positions perçues changées, refus d’aide d’Aubin enregistré ; nouveau devis admissible de la même offre à Gorm, refusée `portee` à 834. |
| 881db69 | 934 → 1393 → 1514 | Aubin arrive, cru en antichambre ; offre d’allumage à Aubin, refusée `marche` à 1414. |
| 881db69 | 1514 → 59112 → 59400 | Ilse crue passée en antichambre, Aubin retrouvé en crypte et nouveaux objets connus ; offre d’allumage à Ilse, acceptée à 59326. |
| 881db69 | 59400 → 59658 → 59944 | Travail payé accompli, engagement retiré ; torche prise et allumée, nouveau bien cessible ; vente à Ilse puis Maël. |
| 881db69 | 59944 → 118741 → 119181 | Torche rachetée à Maël à 118611, possession/droits changés ; vente proposée à Gorm puis aux autres, refus conservés. |

**Verdict limité : réveils justifiés par le contrat observé**, jamais une
empreinte identique réactivée par le délai seul. Aucun défaut commun démontré,
aucun lot de correction moteur proposé. Les entrées citées peuvent être
concomitantes : leur nécessité individuelle n’a pas été éprouvée par retrait.
Le compteur **219** ne certifie aucun suspect dans ces nuits ; il laisse les
deux retours actuels d’agenda en `entree_nouvelle_a_expliquer` (quatre dans
l’historique). Il devrait reconnaître les moyens acquis, les positions
nouvellement apprises et l’engagement effectivement accompli ; compter les
lignes de chronique comme autant de réveils surestime les transitions.

**Preuves : 20 captures avant transition, dont avant chacun des huit réveils**,
monde complet, rendu et scène perçue identiques après sauvegarde/rechargement.
Transitions proposées rapprochées des transitions publiées dans la chronique ;
plans et croyances sans `minute`/`depuis` conservés. Nuits achevées sans
plantage : **50,803 s actuelle, 51,506 s historique** (durées, pas un comparatif
de performance). Bruts : `C:/Users/msics/donjon/artifacts/agenda-268/`,
`actuel/` et `historique-881db69/` : `events`, `plans`, `checks`, `nuit`, `avis`,
`fin.json`, captures et rendus. Aucun calcul actif ; aucune garantie universelle
d’absence de boucle, ni diagnostic des neuf cycles exacts du moteur 218.
