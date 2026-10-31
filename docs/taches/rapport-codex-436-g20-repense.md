# Lot 436 — G20 repensé : contrôler la publication

Conception seule, 31 octobre 2026, laptop. `codex-g20-repense`, base
`integration b21d4656`. Aucun code du jeu modifié, aucun appel au modèle.

**Recommandation : C pour la garantie stricte demandée.** Le direct rend déjà
les signes et impressions. Le manque est la prose qui ajoute un geste, notamment
autour des répliques. Une garde lexicale ne garantit pas l’absence de toute
attribution implicite. C réduit la liberté d’ambiance : décision nécessaire,
restriction non appliquée ici ; G20 reste ouvert.

| Voie | Garantie et limite | Appels, perte joueur, contrôles retirables |
|---|---|---|
| **A — direct + garde de références** | Signes actuels du moteur ; rejet entier du cosmétique mentionnant un PNJ nommé/désigné. Anaphores ambiguës, désignations inédites et attributions implicites restent ouvertes. | Zéro appel direct/garde ; éventuel contrôle de fond G8, sans preuve universelle. Perd des ambiances légitimes et la reformulation des signes. Retrait d’audit sur les seuls rendus moteur. |
| **B — sélection typée Luna (329)** | Rendu actuel recalculé à l’écriture. Ni adoption, ni fidélité de sélection, ni prose adjacente garanties. | Un appel nominal de compilation, zéro audit du rendu typé ; autres audits maintenus. Préserve les questions libres, mais **0 sélection sur 16 requêtes** ; passe 329 : 33 appels dont 14 audits, aucun gain causal établi. |
| **C — composition moteur** | Hors paroles admises et citées, publication de phrases moteur uniquement. Signes recalculés ; ambiance par répertoire environnemental validé, sans emplacement pour texte libre/référence PNJ. Luna peut sélectionner des identifiants admissibles. Garantie structurelle des voies portées, sous réserve du répertoire et de ses conditions. | Zéro appel d’attitude ; ambiance locale zéro, ou au plus un choix en fond, sans relance. Perd l’invention de prose cosmétique ; conserve dialogue inédit admis et création interactive. Audit/extraction/révision retirables seulement des voies portées ; fidélité et admissions restantes conservées. |

**Mesures.** Douze fils : six `signes-*` de `c9459ce` (28 octobre), deux
`attitudes` du 176, quatre `avis-joueur`/`noms-dialogue` de `ca8b8e2` (31 octobre).
Lecture humaine des réponses finales non vides, hors `quitter` : **17/48 avec
attitude présente**, dont **11/38 avec appels**, **6/10 locales**. Portrait,
ignorance et signe passé exclus de cette catégorie.

Prototype A conservateur : toute référence de personne hors citation rejette
le bloc. Sur les 38 réponses avec appels : **32 rejets, 11 avec attitude,
21 sans attitude, zéro attitude manquée**. Neuf des onze sont des signes ou
impressions légitimes à conserver par rendu moteur ; deux ajoutent « Ilse tourne
la tête », sans signe/impression fourni, et sont admises par l’audit comme parole.
Noms/désignations seuls : 30 rejets, dont 19 sans attitude. Ce sont les pertes
d’un filtrage de **réponses assemblées**, pas le taux de faux rejet d’un futur
canal cosmétique séparé : mécanique et paroles admises doivent être préservées.
Les deux ambiances demandées passent, sans attitude. Douze contre-épreuves
**construites et séparées** : A manque quatre des sept attitudes, toutes anonymes
(« Un haussement d’épaules accueille ta proposition ») et bloque trois des cinq
textes sans attitude, dont une anaphore de pierre. Aucun taux général déduit.

Bruts 329 absents du poste : rapport lu sur `origin/codex-g20-signes 19ae7c2e`,
sans recomptage de ses deux contre-exemples. Deux captures bornent le lexique.
**Cinq tests existants verts** : sauvegarde/recharge, Ilse puis Brune, signe
disparu, perte de vue, guet dans deux scénarios ; reprise après blocage initial
des temporaires par le bac à sable. Ils confirment le direct, pas C.
Bruts, annotations, empreintes et commandes :
`C:/Users/msics/donjon/artifacts/g20-repense-436/`.

**Brief de réalisation après décision — invariant unique :** aucun texte libre
du modèle ne devient assertion narrative extérieure aux paroles admises.
Unifier `signes.publics/impressions`, `rendu.regarder`, `Moteur._clore_bilan`
et les sorties descriptives de `MJ` ; conserver la différence consultation pure /
`observer` (trois secondes, lecture éventuelle), sans tirage au rendu.
La saisie libre reste compilable vers ces actions existantes, avec fidélité à vérifier.
Dans `narration.consigner` et `repliques_moteur`, composer les citations admises
avec leur locuteur moteur, sans didascalie libre ; vérifier la provenance réelle.
G8 porte ensuite `narrateur.py` vers le répertoire conditionné par la projection
publique, sans activation avant G9–G11/U-A. Les voies non portées gardent leurs
contrôles. Vérifier Gorm/Aubin du 329, Ilse ci-dessus et un autre PNJ, monde
et affichage rechargés, signe périmé avant écriture, inconnus, formulations
anonymes, citation conservée sans geste, fragment inconnu/périmé, sauvegarde
avant affichage et abandon entier. Tests ciblés et une passe Luna
`signes-*`/`attitudes`/`noms-dialogue`, aucune consigne d’exemples ajoutée.

**Question unique : acceptez-vous de limiter l’ambiance publiée à un répertoire
environnemental validé (C, recommandé pour garantir l’absence d’attitude inventée),
plutôt que conserver une prose libre dont A ne garantit que les références reconnues ?**
