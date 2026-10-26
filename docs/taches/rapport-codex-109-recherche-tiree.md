# Lot 109 — coût de la recherche tirée (2026-10-26)

Branche `codex-recherche-tiree`, **non fusionnée**, base **70f4fae**.
**Diagnostic seul : arrêt avant implémentation, aucun moteur ni scénario modifié.**

**Protocole.** Auberge 1985, départs tiré et fixe, `42bb9c0` contre la base
actuelle : nuits propres de 12 h, fenêtre 480–720, deux processus appariés à
priorité réduite, poste partagé. Une phase `cProfile(process_time)`, puis des
témoins détaillés sans profileur, compteurs actifs ; aucun cache de temps, aucun Luna. Les
générations sont les appels réels à `gestes`, hors listes reprises du graphe ;
les nœuds du diagnostic désignent le résultat de la dernière passe.

**Le tiré explore davantage que le fixe actuel ; ses générations sont moins
chères.** Sur la fenêtre :

| Version / départ | Recherches | Nœuds consignés / recherche | Générations / recherche | Gestes bruts / génération | Génération-normalisation, µs / génération¹ |
|---|---:|---:|---:|---:|---:|
| Ancien fixe | 4 020 | 220,7 | 85,4 | 7,95 | 971 |
| Actuel fixe | 6 350 | 43,5 | 35,1 | 7,91 | 1 848 |
| Ancien tiré | 2 517 | 240,6 | 105,0 | 8,16 | 911 |
| Actuel tiré | 4 674 | 115,5 | 119,8 | 8,14 | 1 244 |

¹ Cumul inclusif de `_suites`, instrumentation comprise, non additionnable
aux sous-fonctions. Tiré/fixe actuel : **×3,42 générations par recherche**,
**−32,7 % par génération** ; **×2,52 générations au total** malgré moins de
recherches. Ancien→actuel tiré : moins de nœuds consignés, mais **×2,12 listes
régénérées**, **+36,6 % par génération**. Les deux effets existent ; compter
seulement les nœuds du résultat masquerait le travail réel. Toutes passes
principales, ancien→actuel tiré : **605 597→543 274 nœuds**,
**240,6→116,2 par recherche**, **102,7→392,9 µs CPU/nœud** sans profileur
(CPU de `chercher`, préparation et certificats compris). Certificats séparés :
**11 428→86 027 nœuds**. Suites retenues par normalisation principale :
**4,61→5,30** ; les devis différés normalisés hors `_suites` ne sont pas comptés.

Le tiré actuel concentre les générations sur **Tilo/faim : 195 291** (fixe
50 930 ; ancien tiré 14 174), **Joss/faim : 86 269**, **Lucien/garder:grenier :
73 555**, **Lucien/placer:ballot : 57 229**, **Mathurine/faim : 51 522**.
Les familles brutes ancien→actuel tiré : aller **1 863 461→3 925 561**,
ouvrir **3 089→93 852**, manger **774→156 114**, prendre **54 855→71 495**,
acheter **34 306→318** ; 40 107 suites différées actuelles, dont les gestes
révélés sont normalisés séparément. Les tableaux par PNJ/but comprennent
nombres, nœuds, CPU, quantiles et issues dans `bilan.json`.

L'écart unitaire ancien→actuel porte notamment les approches et leur
composition : `_mesurer` **147,84 s inclusives**, normalisation **39,03 s
propres**, `Etat.apres` **27,95**, `arrivee` **18,38**, `mesure_aller` **16,67**,
`prix_route` **12,53** ; `gestes` **90,91 s propres**. Les cumuls sont emboîtés.
Ces lectures dépendent de l'état projeté ; aucune lecture dominante constante
par Vue n'est établie par ce profil.

À 8 h, Lucien fixe est à l'étable avec lanterne, huile et crochets ; Lucien
tiré au grenier porte la besace d'Anselme et sa clé, sans lanterne. Anselme
tiré porte les crochets, le bois de cuisine et quatre parts de réserve,
contre trois en fixe ; Mireille fixe détient la quatrième. Hugues est à la
salle commune en tiré, en cuisine en fixe. Ces mondes et besoins différents
interdisent une attribution causale à une seule modification du moteur.

**Levier principal et décision.** Les passes offrant les deux allures
(15/30, ordinaire et feutrée) portent **380 850 nœuds**, **332 059 générations**,
**124,28 s CPU**, soit **58 % du CPU de `chercher`** dans le tiré actuel.
Tilo/faim : **105 passes, 155 194 nœuds, 58,86 s** ; Lucien/garde-grenier
**29,92 s**, placement **24,64 s**. Ce sont des passes offrant les deux
allures, pas un comptage des seuls états feutrés. Les reprises de découverte
ne totalisent que 4 628 nœuds : les supprimer seules ne traite pas ce volume.
Retirer ou borner l'exploration des allures et moyens peut supprimer un plan
admissible sans témoin et changer une décision ; aucune preuve d'identité ne
l'autorise. Arrêt demandé
par le brief : aucun nouvel élagage, cache moteur ou micro-levier secondaire
implémenté. La cadence des recherches reste hors du lot.

**CPU sans profileur.** Fixe 12 h : **121,47→218,84 s (×1,80)** ; tranche :
**96,63→143,50 s**. Tiré : **102,53→277,31 s (×2,70)** ; tranche :
**77,22→235,83 s**. Rapports des témoins avec compteurs, sans nouvelle
mesure CPU nue ; aucun gain ni résultat levant le seuil ×1,5 manqué au lot 105
(×1,75 fixe / ×2,67 tiré). Toutes passes
actuelles, fixe→tiré : **43,6→116,2 nœuds/recherche**, **418,5→392,9 µs/nœud**.
Le tiré développe donc **×2,67 états/recherche**, légèrement moins chers.

**Contrôles et limites.** Les quatre nuits ont les mêmes traces de
recherche, gestes, diagnostics hors durée et mondes à 480/720 entre profil
et témoin ; huit recharges (monde, `regarder`, `scene_percue`) correctes.
SHA-256 de tous les modules moteur inchangés. Empreintes quatre scénarios,
`VERIFIER`, mine, `comparer --calcul` et suite complète non lancés :
vérifications conditionnées à une implémentation, arrêt prescrit au diagnostic.
Reproduction : `campagne_recherche_109.py --phase profil`, puis `--phase detail`,
et `bilan_recherche_109.py artifacts/recherche-109` ; archive locale de
`42bb9c0`, bruts et captures dans `artifacts/recherche-109/`. Une graine,
pas de preuve statistique ni de garantie générale d'invariance. Créneau de
45 minutes consacré à la mesure et à sa livraison.
