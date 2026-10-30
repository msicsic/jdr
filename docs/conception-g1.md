# G1 : conserver le sens avant de réduire le contexte

29 octobre 2026 — lot 318, conception seule, branche `codex-g1-repense`,
base `integration 79fca6a`. **Recommandation : suspendre le portage compact
actuel, préparer U-P/U-C sur les contrats existants, puis reprendre G1 sous
la forme A ci-dessous.** Ce n'est ni une cinquième reprise de la branche
`codex-g1-compilateur`, ni une autorisation de retirer les contrôles actuels.
La feuille de route et le contrat du MJ restent inchangés jusqu'à décision.

## 1. Ce que les archives permettent de conclure

Le petit contexte a retiré des explications utiles, mais **les pertes ne
s'expliquent pas toutes par des informations absentes**. Dans plusieurs cas,
la bonne opération, ses paramètres et ses références figurent dans la requête.
Le compilateur les ignore, puis la correction ou la revue aggrave l'écart.
Remettre une phrase de prompt pour chaque saisie échouée reproduirait les
quatre reprises sans garantir le contrat commun.

Corpus lu sans réseau : les six scripts `avis-joueur`, `crypte`, `echanges`,
`relais`, `ressources`, `soir-appel` des lots 294, 296, 304 et 311, plus leur
référence commune `230e7b3`. Chaque variante contient **91 saisies hors sortie,
30 tours avec modèle et 61 sans modèle**. Ce sont les mêmes 91 positions de
script, pas 364 intentions indépendantes ni quatre répétitions à code constant.
Les versions intermédiaires ont aussi intégré des changements d'intégration.
Une seule passe par version ne mesure pas la probabilité d'une variance Luna.

Lecture des requêtes complètes (`instructions`, `entree`, `schema`), des
charges retournées, des revues, des refus et du texte publié. Les rapports
[294](https://github.com/msicsic/jdr/blob/codex-g1-compilateur/docs/taches/rapport-codex-294-g1-compilateur.md),
[296](https://github.com/msicsic/jdr/blob/codex-g1-compilateur/docs/taches/rapport-codex-296-g1b-fidelite.md),
[304](https://github.com/msicsic/jdr/blob/codex-g1-compilateur/docs/taches/rapport-codex-304-g1c-familles.md) et
[311](https://github.com/msicsic/jdr/blob/codex-g1-compilateur/docs/taches/rapport-codex-311-g1d-revue.md)
ont été lus sur `origin/codex-g1-compilateur`. Les copies de
lecture et les preuves sont dans `C:/Users/msics/donjon/artifacts/g1-318/`.

Le fichier `saisies.json` contient les 91 lignes avec les quatre résultats,
la référence, les propositions, refus et états publics archivés ;
`lecture-fils.md` restitue les appels décodés des 30 tours ;
`charges.json` conserve leurs requêtes complètes ; `preuves-contrats.json`
localise les champs discutés ci-dessous. `sources-sha256.json` identifie les
fils lus. Les sources ont la même empreinte après lecture.
Les scripts `lire_archives.py` et `preuves.py` n'importent pas le jeu.
**Aucun rejeu moteur, test, banc ou appel Luna dans ce lot.**

Les états de tour des fils sont des projections, pas des sauvegardes
intégrales. Les preuves de recharge de prix et d'odeur des anciens lots sont
réutilisées ; aucune nouvelle garantie de chaîne monde/rendu/recharge n'est
déduite d'un JSON valide ou d'un verdict de revue.

### Mesures historiques et dénominateurs

| Mesure | Référence | 294 | 296 | 304 | 311 |
|---|---:|---:|---:|---:|---:|
| Admissions au premier coup / 30 | 22 | 18 | 23 | 23 | 21 |
| Appels totaux / 30 tours | 99 | 98 | 100 | 115 | 104 |
| Appels par tour | 3,30 | 3,27 | 3,33 | 3,83 | 3,47 |
| Abandons formels hors obstacles réels | 1 | 3 | 1 | 0 | 3 |
| Entrée fournisseur moyenne, jetons/compilation avec reprises | 22 572 | 11 082 | 13 252 | 13 657 | 13 858 |
| Préfixe caché moyen, jetons/compilation | 11 812 | 4 700 | 4 638 | 5 517 | 5 113 |
| Secondes modèle par tour | 9,82 | 9,95 | 8,02 | 8,48 | 7,71 |

Les temps de référence viennent du cache : **aucun gain causal de vitesse**.
Le 311 compte 57 → 55 appels de réponse, 15 → 21 revues et 27 → 28 audits :
la réduction d'entrée ne réduit pas le nombre total d'allers-retours.
Les scores de fidélité des 294–304 excluent les refus fidèles et ne sont pas
comparables au score du 311. Celui-ci crédite l'intention entière conservée
par un refus moteur : **27 → 23 finales, 23 → 20 au premier coup**. Les
agrégats 20 → 20 des 296/304 ne démontrent aucune stabilité par famille.
L'absence d'abandon formel au 304 masque des intentions éludées.

## 2. Diagnostic saisie par saisie

Indices zéro. Dans les tableaux : **E** = donnée/provenance retirée de l'entrée ;
**C** = consigne retirée, ambiguë ou concurrencée ; **S** = schéma qui permet
une opération voisine ou omet une contrainte de sens ; **R−** = revue trop
stricte ; **R+** = revue trop permissive ; **V?** = variation de choix malgré
un contrat disponible, cause exacte indécidable sans expérience contrôlée.
Ces causes peuvent se cumuler. « Présent dans le schéma » prouve une
disponibilité, jamais que Luna en a tenu compte. Les influences C/S sont des
explications de conception étayées par les fils, pas des effets causaux isolés.

Pour retrouver une preuve : choisir le script et `tours[n]` dans le fichier
du lot indiqué par `sources-sha256.json`, puis `fil` ; les entrées décodées
sont rangées sous `lot:lot-r1:script/n` dans `charges.json`.
Les tours à zéro appel sont tous répertoriés en annexe.

### Les trente tours avec modèle

| Saisie | 294 | 296 | 304 | 311 | Cause et information nécessaire |
|---|---|---|---|---|---|
| `avis-joueur/0` « je dis à Gorm : l'eau va gagner la conduite basse » | Avis conservé | Conservé | Conservé | Conservé | Aucun retrait nécessaire démontré. Adresse, lieu et valeur sont présents. Les écarts d'appels viennent surtout du récit/audit après parole. |
| `avis-joueur/1` « je dis à Gorm : l'eau va gagner la galerie de ronde » | Avis conservé | Conservé | Conservé | Conservé | Même contrat ; ne pas classer les relances de prose comme erreurs de compilation. |
| `avis-joueur/2` « à tous : l'eau ne menace pas le refuge du relais » | Avis négatif conservé | Conservé | Conservé | Conservé | Adresse collective et négation conservées. Les mots entendus n'établissent pas la vérité de l'avis. |
| `crypte/1` « il fait sombre ici ? » | Question prononcée par Corvus | Dialogue fidèle | Dialogue fidèle | Dialogue fidèle | C/S : `parole_prevue` fournissait une audience possible sans décision de parler ; pas de manque d'éclairage établi. Le 296 ajoute la forme de saisie ; le 311 distingue `parole_possible`. |
| `crypte/8` « que représente la gravure ? » | Figure décrite | Figure et inscription | Conservé | Conservé | Détail déjà connu accessible ; aucune perte d'intention démontrée, ni besoin d'un savoir secret pour expliquer l'énigme. |
| `crypte/9` « j'écoute à la porte pour savoir s'il y a quelque chose derrière » | Bonne écoute refusée, puis gestes étrangers | Écoute exécutée | Bonne écoute refusée puis acceptée | Écoute exécutée | R−/V? : `ecouter` sans cible est le contrat moteur, déjà dans les consignes. Le dossier de revue ne rendait pas assez explicite sa portée. La référence elle-même perd l'écoute. Ce n'est pas une opération absente du petit contexte. |
| `crypte/10` « je glisse mon couteau sous la tête de l'axe supérieur et fais levier » | `detacher/axe_haut/couteau/levier` | Même geste | Même geste | Deux `impossible`, abandon et texte interne publié | C/S/V? : l'ancienne explication détaillée des fixations est abrégée, mais `detacher`, `levier`, l'axe amovible et le couteau `levier_fin` sont encore fournis. Le manque d'opération affirmé est faux ; la correction prend la proposition refusée pour une autorité. Voir 2.1. |
| `crypte/23` « Gorm, que sais-tu de cette crypte ? » | Parole et réponse | Conservées | Conservées | Conservées | Aucune perte démontrée. Savoirs autorisés du répondant et mots effectivement entendus restent des contrats nécessaires, distincts de ses secrets. |
| `crypte/24` « Gorm, combien me donnes-tu pour l'anneau ? » | Mission vide puis `negocier/0`, prime 22 | `negocier/0`, prime 22 | `propos`, prime 20 | `propos`, prime 20 | C/S : confusion consultation/amélioration ; mission et offre de 20 déjà présentes dans toutes les entrées. Au 296, même la description du zéro-plafond est présente. Au 304/311, `prix` existe mais n'est pas choisi. Montant réparé, typage de consultation non démontré. |
| `crypte/25` « décris-moi l'échoppe » | Description reprise | Description conservée | Conservée sans reprise | Conservée après reprise | Pas de donnée manquante établie ; variations de prose/audit. Garder aspect connu et provenance publique pour la description transitoire, pas tout le dossier social privé. |
| `crypte/26` « J'attends que Gorm ait le dos tourné pour prendre discrètement les crochets » | Improvisation qui invente son orientation | Éteindre puis fermer la lanterne | `voler/finesse`, refus de proximité fidèle | `voler/simple`, refus exact mais attente omise | C/S puis R+ : deux clauses, attente et transfert discret. Au 294, la règle détaillée `patienter` a quitté les consignes, l'opération reste dans l'enum. Au 296–311, son sens est décrit dans le schéma. La revue du 311 réduit à tort l'attente à une manière. Aucun droit d'inventer l'orientation de Gorm. |
| `crypte/41` « qu'est-ce qu'il y a derrière la porte, selon toi ? » | Métacommentaire puis ignorance perceptible | Avis sur lieu inconnu puis dialogue repris | Question devenue parole/avis | Avis sur lieu inconnu puis dialogue sans parole | C/S, R+ au 304, V? : confusion question au MJ/avis émis par Corvus. La forme non explicitement parlée est connue dès 296 et l'audience seulement conditionnelle au 311. Le lieu inconnu est un refus correct d'une proposition étrangère, pas une intention impossible. |
| `echanges/1` « bonsoir, vous tenez le coup ? » | Question entendue | Conservée | Conservée | Conservée | Conversation ordinaire maintenue ; aucun retrait de données démontré. Ne pas créditer un effet social supplémentaire non typé. |
| `echanges/2` « Tu sais où est passé le gardien ? » | Localisation d'une personne inconnue, puis abandon technique | Sujet libre prononcé | Conservé | Conservé | C/S : le rôle est un sujet de parole, pas une identité connue. Référence et 294 commencent par le même candidat invalide ; seule la référence récupère `propos`. Ce n'est pas la suppression d'une identité qui était connue. |
| `echanges/3` « je dis à tous que l'eau monte et qu'il faut garder le feu » | Avis et propos | Avis déclaré mais absent, corrigé | Avis et propos | Avis et propos | S/R+ potentiel : les mots seuls ne couvrent pas l'avis ; contrôle déterministe utile au 296. « Garder le feu » demeure prononcé, sans engagement à entretenir le brasero créé par cette phrase. |
| `relais/1` « ça sent quoi, ici ? » | Question devenue parole | Odeur éludée | Odeur éludée | Odeur décrite, enregistrée et relue | C/S : permission commune d'ambiance omise, puis restaurée au 311. Pas de source olfactive établie supprimée démontrée ; une odeur cosmétique peut être proposée sans devenir entité. Audience possible et décision de parole étaient confondues au 294. |
| `relais/2` « je fredonne doucement » | Expression sans effet son, correction de difficulté | Son toujours absent malgré revue conforme | Son récupéré en trois charges ; jet CHA 10 | Son récupéré ; effort/CHA 10, confirmation | C/S et R+ : l'ancien contrat autorise le geste simple sans jet et exige l'effet sonore. Les schémas ultérieurs expliquent ces points mais autorisent toujours CHA/effets vides. Le bruit et le récit ne remplacent pas une émission. Aucun son exécuté au tour dans les quatre lots, contre la référence. |
| `relais/4` « que dit la consigne, exactement ? » | Nouvelle lecture INT 12/2 min, non exécutée | Citation exacte sans geste | Conservée | Conservée | E/C/R+ : `evenements_recents` retiré au 294 ; toutefois le texte reste dans `objet:gravure.inscription` ET la conversation. C'est la preuve canonique de lecture passée qui manque, pas le texte. La revue admet la relecture superflue. Voir 2.1. |
| `relais/5` « je cherche des traces de pas sur le sol » | Examen du sol | Examen du sol | Examen du sol | Examen du sol | Recherche distincte non certifiée dans les cinq variantes. Aucun succès ni déficit attribuable au seul G1 ; ne pas inventer une garantie de recherche à partir de `examiner`. |
| `relais/19` « décris-moi l'ambiance de cette conduite » | Trois proses, positions/sources corrigées | Description admise | Description admise | Deux proses, ambiance finale admise | E/C/V? : aspect d'auteur et coordonnées retirés, localisation publique gardée. La première prose 294 reconstruit mal présence/orientation et lumière. Pas de preuve que restituer les coordonnées aurait suffi ; ces faits doivent être rendus par le moteur, ambiance séparée. |
| `relais/20` « est-ce que je pourrais passer sous la poutre effondrée ? » | `franchir`, puis passage mal référencé/improvisation | `franchir`, corrigé en `passer_obstacle/dessous`, refus réel | `franchir`, puis bon passage rejeté car non admis, dialogue | Deux `faufiler/sud`, abandon | C/S, R− au 304 : `franchir` concerne l'assemblage installé, `faufiler` un pas ; seule la séquence porte `passer_obstacle`. Au 296–311 le schéma explique la distinction et le souvenir est fourni. Deux refus de sens justes au 311 ne récupèrent pas l'intention. |
| `relais/21` « je donne un coup de pied dans la poutre » | Nom littéral puis référence, refus parasite | Même dérive de référence | Faux refus « non admis = absent », percussion mal référencée | Poussée étrangère puis improvisation rejetée pour manière absente du dossier | C/S/R− : le souvenir identifie la cible, mais cible textuelle/identifiant sont confondus. Au 311 la première revue est juste, la seconde ne reçoit plus l'intention ni les récits du geste improvisé. Ce défaut de dossier est établi ; ajouter « coup de pied » au prompt ne le répare pas. |
| `relais/22` « je prends le pied-de-biche » | Pied-de-biche remplacé par brasero | Même substitution | Dialogue, cible vide, puis cible littérale ; six appels | Cible demandée et refus public fidèles | C/S/R− au 304 : aucune référence à ce bien n'est disponible ici ; il faut conserver la désignation non résolue pour le moteur, pas inventer un id ou choisir un objet visible voisin. La référence aussi hésite avec `impossible`. |
| `ressources/0` « Aubin, as-tu du bois ? » | Ressource demandée | Conservée | Conservée | Conservée | Adresse et catégorie ressource conservées ; variations après compilation. Aucun besoin d'inventaire caché du PNJ pour poser la question. |
| `ressources/1` « je demande à Brune si elle a de quoi manger » | Ressource demandée | Conservée | Conservée | Conservée | Même contrat public ; réponse et refus restent ceux du moteur. |
| `ressources/2` « Aubin, tu me dois quelque chose ? » | Réclamation typée | Conservée | Conservée | Conservée | Rôles et sens du dû conservés ; ne pas déduire paiement de la question. |
| `soir-appel/2` « est-ce que quelqu'un a du bois ? » | Demande collective | Conservée | Conservée | Conservée | Adresse collective conservée ; le nombre d'appels de récit n'indique pas une perte de compilation. |
| `soir-appel/3` « as-tu de quoi manger, Ilse ? » | Ressource demandée | Conservée | Conservée | Conservée | Identité publique et ressource conservées. |
| `soir-appel/4` « je réclame à Aubin les deux pièces qu'il me doit » | Réclamation conservée | Conservée | Conservée | Conservée | Rôles et deux pièces conservés ; richesse de réaction à vérifier séparément des mots. |
| `soir-appel/5` « je paie Aubin trois pièces pour une de ses planches » | Réplique vide, nom littéral, part devenue objet ; abandon | Part `planches` contre 3 pièces | Conservée | Conservée | C/S : référence publique `planches`, unité part et contrepartie typée nécessaires, toutes déjà disponibles. Les descriptions du 296 les rendent explicites. Le refus commercial ultérieur est une issue fidèle, pas un abandon de l'intention. |

### 2.1. Les retraits établis et les faux diagnostics de manque

- **Provenance du rappel, 294 `relais/4`.** Le premier appel contient encore
  la consigne exacte à `entree.faits.objet:gravure.inscription` et
  `entree.conversation[2].reponse`. Il ne contient plus
  `faits.evenements_recents`, où la référence atteste l'examen effectué au
  tour précédent. Les 296/304/311 rétablissent cette preuve et rendent la
  citation. Le retrait de provenance est établi ; sa causalité exclusive ne
  l'est pas, puisque les consignes ont aussi changé. Dire « le petit contexte
  avait perdu le texte » serait faux.
- **Geste simple et son.** La référence explique « stat vide, difficulté 0 »
  pour l'expression simple, puis les paramètres de `son`. Le 294 abrège ces
  consignes ; les enums restent disponibles. Les versions suivantes replacent
  les descriptions dans le schéma, mais Luna choisit encore un jet et oublie
  l'effet. Information et saillance ont été réduites ; le déficit persistant
  n'est pas une donnée du monde manquante.
- **Passage et attente.** L'ancienne consigne explique `passer_obstacle` et
  `patienter` ; le premier petit prompt ne les explique plus. Au 296–311,
  `proposition.anyOf[1].properties.etapes.items.properties.operation.description`
  contient ces contrats, dont l'attente de deux minutes sans orientation
  imposée au tiers. Les pertes du 311 surviennent donc malgré leur présence.
- **Levier, 311 `crypte/10`, premier appel.** L'enum de l'action contient
  `detacher`, celui de méthode `levier` ; `objet:axe_haut` dit amovible,
  attaché, extraction par outil, à portée ; `objet:couteau` est porté et
  possède `levier_fin`. La relation détaillée outil/méthode/risque est moins
  expliquée qu'avant, mais l'opération n'a pas disparu. Le second appel
  attribue au « retour » l'absence d'opération que le modèle avait lui-même
  affirmée. Puis l'audit publie cette justification comme source mécanique.
- **Prix.** `missions_discutables.anneau_veilleur.offre.contrepartie.montant`
  vaut 20 dans les cinq premières requêtes. Ce n'est pas une information
  retirée. `negocier/0` portait une ambiguïté mécanique réelle, explicitée
  au 296 puis séparée de la consultation au 304. Le 304/311 sauve le montant
  par `propos` et l'offre moteur existante ; il ne démontre pas l'usage de
  `conversation_pnj/prix`.

Le **schéma demeure permissif entre opérations** : un nom d'action parmi
plusieurs, une cible string, une méthode parmi plusieurs, des effets sonores
facultatifs ; l'assemblage légal de champs n'est pas forcément le bon geste.
`mode` et `proposition.anyOf` sont aussi indépendants. La description générale
« utilise les références exactes » concurrence le besoin de conserver une
désignation absente. Ce sont des défauts de contrat de représentation, pas
des raisons de filtrer les actions selon un objet ou un mot de la saisie.

### 2.2. Revues : deux erreurs opposées

La revue du 304 infère parfois « non admis » → « aucun geste prévu » ; ailleurs
elle admet pour le même motif l'absence de tout écart. Une proposition sur
copie reste analysable pour son sens, même refusée par le monde.
Le 311 élimine ces motifs, pas toutes les erreurs :

- `relais/20` : les deux `faufiler/sud` sont correctement refusés, mais la
  correction renvoie le même geste. Une bonne revue ne garantit pas la reprise.
- `relais/21`, seconde revue : `plan.proposition` garde approche, cibles et
  effets, mais retire `intention` et les récits. La demande originale reste
  présente. La revue exige alors le coup de pied absent de son propre dossier.
  Elle doit disposer du sens proposé sans traiter les brouillons comme effets.
- `crypte/26` : la proposition et sa justification disent attendre, mais
  `voler/simple` ne compile que le transfert ; `finesse` ajoute `patienter`.
  La revue accepte l'omission parce qu'il n'y aurait pas d'effet « durable ».
  Une condition, une durée ou un ordre sont pourtant des clauses de gameplay.

Une grille commune doit comparer **modalité, acte, cible, moyen, unité,
quantité/prix, ordre, attente/condition, audience et consentement** au plan
canonique développé. Les événements transitoires comptent aussi. Cette grille
ne peut pas prouver toute équivalence d'une phrase libre ; le joueur garde
le contrôle par U-P/U-C et les revues transitoires restent jusqu'à décision.

## 3. Ce que G1 doit garder, ce qu'il peut laisser

Invariant proposé : **toute proposition conserve la modalité et toutes les
clauses de l'intention jusqu'au plan présenté, au verdict moteur et à la
recharge ; une réduction d'entrée n'efface ni les données nécessaires à la
désignation, ni le sens des opérations exposées.** La fidélité sémantique
reste mesurée, elle n'est pas garantie par la seule validation déterministe.

| Élément de l'ancienne interprétation | À garder dans le contrat commun | À laisser hors du compilateur, et preuve/limite |
|---|---|---|
| Contexte public et mémoire | Références et alias publics, actuel/souvenir, portée connue, inscriptions connues et preuve datée d'acquisition, paroles entendues avec auteur, dernier essai et plan en attente | Coordonnées internes redondantes et prose d'auteur peuvent sortir si leur information utile a une projection publique équivalente ; pas de preuve d'équivalence générale aujourd'hui. `relais/4,20,21` interdisent une liste arbitraire de champs supprimés. |
| Historique de conversation | Référents, question encore pendante, clauses corrigées ; paroles réelles séparées des brouillons | Pas besoin de toute la conversation pour tout geste ; aucune ablation archivée ne prouve qu'un résumé suffit. Le conserver au premier portage ; réduire seulement après contrôle de dépendances, sans résumer une preuve de lecture en impression. |
| Sens des actions | Préconditions publiques de désignation, paramètres admissibles, expansion des raccourcis, conditions/ordre, caractère sans jet d'une expression simple | Retirer les longues explications littéraires et doublons, pas les contrats `patienter`, son, passage, fixation. Les décrire depuis un registre partagé par moteur, schéma, plan et interfaces ; ni nouveau dictionnaire de formulations ni liste d'exemples dans le prompt. |
| Modalité | Question au MJ, faisabilité, action demandée, parole de Corvus, consultation/offre/accord distincts ; audience possible conditionnelle | Ne pas faire décider le mode par la seule présence d'un PNJ, d'une offre ou du mot « avis ». `crypte/1,24,41` montrent ces substitutions. Les marqueurs déterministes actuels sont des indices, pas un analyseur sémantique complet. |
| Social | Termes et rôles, part/objet/pièces, montant, mots imposés, adresse publique, offre existante et état d'accord | Les secrets du PNJ et ses inventaires cachés ne servent pas à comprendre une demande de ressource. Leur retrait ne doit pas retirer la voie sociale ni ses raisons moteur. Les sept tours ressources/comptes/marché et les avis en témoignent. |
| Invention | Catalogues publics d'admission, fait/qualification demandé, support et geste à reprendre après admission | Le compilateur ne fournit ni indice, ni orientation de tiers, ni nouvelle capacité favorable. Les six scripts n'exercent pas assez l'invention admise pour valider cet axe. Les voies et revues actuelles restent. |
| Correction | Saisie originale, candidat précédent marqué non admis, refus moteur avec `attendu`, clauses du plan initial toujours comparables | Une justification Luna n'est jamais une règle moteur. Ni changement de cible pour passer la validation (`relais/22`), ni réparation du seul champ d'une action étrangère (`crypte/26` au 296). Garder la borne de correction existante ; ne pas l'allonger pour gagner le banc. |
| Rendu et persistance | Résultat et refus publics du moteur, provenance, sauvegarde avant affichage, même plan après recharge | Retirer explication libre du refus et reformulation mécanique déjà remplacées par G2/G4. Garder les contrôles de perception, PNJ et description non encore portés. Le texte interne du 311 prouve qu'un audit ne transforme pas une proposition en vérité moteur. |
| Style et ambiance | Demande identifiable, faits connus conservés pour sa voie transitoire, publication séparée selon le contrat adopté | Ton, 2–5 phrases, aspect et odeur n'ont pas à diriger les plans d'action. Transférer la cosmétique à G8–G11/G14, sans supprimer sa demande ni activer prématurément le fond. La récupération d'odeur du 311 ne certifie pas ce futur canal. |

Le sens des méthodes appartient au moteur : un registre commun peut exposer
que tel raccourci contient une attente et qu'un autre n'en contient pas,
sans lui faire inférer les mots du joueur. Un identifiant résolu et une
désignation non résolue sont deux valeurs distinctes ; cette dernière garde
le texte original et aboutit à un refus ou une clarification moteur, sans
inventer un identifiant ni un objet. Le transport de cette distinction est
à concevoir dans le lot dédié, pas un effet nouveau admis au passage.

## 4. Ce que les interfaces fusionnées retirent réellement du libre

État considéré : `79fca6a`. U-D 293, U-T premier geste 299, U-M inventaire
298, outils 300, fabrication 305 et U-T inventaire 301 sont fusionnés.
U-T outils 307, corps, passages et social ne le sont pas à cette base.

| Lots livrés | Preuve existante d'accès sans compilation | Limite pour G1 |
|---|---|---|
| U-D 293 | 17 cas ; références exactes, homonymes et périmés ; zéro modèle. Dans 16 cas, le texte équivalent faisait déjà zéro appel ; seul l'examen du PNJ sans portrait évite un renvoi MJ observé | Transport de l'intention choisie, pas couverture de toutes les formulations libres. « Lui parler » reste libre. |
| U-T 299 | 14 couples objet/porte ; 3 touches, 4 avec F7, contre 17–27 pour la commande à référence | Les gestes simples du catalogue sont accessibles au terminal ; pas les paramètres d'outils, les passages ou le social. |
| U-M 298 et U-T 301 | Dix parcours web : 2 clics, 3 pour la remise ; 24 parcours terminal : 3 touches, 4 avec F7 ; zéro modèle | Poser/remettre le lot entier, manger/prélever une unité, lumière portée. Destinataire vu à portée ; pas d'identité devinée, de quantité libre ni de contenu fermé révélé. |
| U-M outils 300 | Dix parcours : 3 clics avec cible déjà à portée, zéro modèle | Choix d'outil, clé, combustible et destination pour les gestes offerts ; aucun `detacher/levier` ni vol conditionnel livré par ce lot. Le menu « frapper avec » ne prouve pas la fidélité d'un coup de pied sans outil. |
| U-M fabrication 305 | Quatre commandes composées évitées : 17 clics/assemblage, 8/découpe, dimensions saisies en sus ; zéro modèle | Échelle connue et découpe ; pas l'aperçu de faisabilité, une qualification inconnue, l'approche de matériaux éloignés ou un objectif composé. |

Sources : rapports [293](taches/rapport-codex-293-ud-descripteur.md),
[298](taches/rapport-codex-298-um-inventaire.md),
[299](taches/rapport-codex-299-ut-premier-geste.md),
[300](taches/rapport-codex-300-um-outils.md),
[301](taches/rapport-codex-301-ut-inventaire.md) et
[305](taches/rapport-codex-305-um-fabrication.md). Ce sont des mesures de
parcours déterministes distincts ; **ne pas additionner leurs tailles** pour
annoncer un nombre de tours MJ supprimés.

Le classement du [288, section 3](conception-valeur-llm.md#3-saisies-réelles--701--de-gestes-simples-un-potentiel-social-distinct)
portait sur 184 positions, 368 saisies et 187 tours MJ historiques.
Ses **70,1 % de gestes simples**, ou **82,1 % avec social structurable**,
étaient un potentiel d'interface, pas la couverture fusionnée.
Recomptage des lignes `acces=m` : **15 positions / 30 saisies** relèvent des
verbes de menu déjà recensés au 288, dont **12 tours MJ et 30 appels
historiques**. Ce volume n'est pas un gain U-D : beaucoup de commandes
étaient locales et G4 a déjà retiré leur narration. La disponibilité des
cibles n'a pas été rejouée. `menus-288.json` donne les lignes exactes.

Dans les six scripts G1, le seul équivalent évident parmi les trente tours
MJ par un verbe d'objet fusionné est `crypte/8` → examen de la gravure
connue, déjà examinée au tour 7 ; ce n'est pas une réussite de clic mesurée.
`crypte/1` peut consulter la lumière par une commande existante, sans gain
attribuable aux nouveaux menus. `relais/4` demande un **rappel exact**, pas
une nouvelle lecture ; `relais/5` n'a pas de recherche certifiée ; le
pied-de-biche absent en `relais/22` ne peut pas être une cible de menu.
Les trois dialogues ressources, les trois avis, le marché, le levier,
l'attente/vol et le passage ne sont pas supprimés du libre par ces lots.
Les deux remises des six scripts ont déjà zéro appel et échouent sur une
identité inconnue ou un destinataire hors de vue ; leur ajouter un bouton
ne doit pas les transformer en remises réussies.

L'extrait des six scripts est donc surtout un banc des **difficultés
résiduelles**, pas un échantillon de fréquence d'usage. Les menus réduisent
le besoin pratique de phrases pour les gestes usuels ; ils ne rendent pas
ces phrases fidèles et ne permettent pas d'abaisser le dénominateur de G1
sans conserver une mesure de couverture de toutes les intentions.

## 5. Deux formes possibles, au plus

### A — Compilateur général à contexte public conservateur

**Périmètre : toutes les saisies libres qui atteignent aujourd'hui le MJ**,
y compris gestes simples, questions au MJ, compositions, paroles,
négociation, demandes de faits et de qualifications. Les commandes et
descripteurs structurés passent directement au moteur. Les voies non encore
portées conservent leur implémentation et leurs contrôles pendant la migration.
La cible n'est plus « le plus petit contexte », mais « aucune dépendance
utile supprimée ». Les descriptions et l'ambiance restent distinctes des
propositions à effets, selon leur portage.

Un appel nominal propose le mode et un plan exprimable avec les contrats
canoniques. Le schéma corrèle le mode à sa charge et chaque opération à ses
paramètres. Un registre du moteur décrit leur sens, expansion et effets
typés, réutilisé par le schéma, U-P et les interfaces. Il n'invente aucune
mécanique et ne sélectionne pas les opérations sur un mot de la saisie.
Les conditions non représentables restent explicites ; elles ne deviennent
ni une réussite fictive ni une clause silencieusement effacée.

Le contexte initial conserve les données publiques de l'interprétation
actuelle : seuls les secrets et les doublons dont l'équivalence est prouvée
sont exclus. L'optimisation intervient après fidélité, par dépendances du
contrat exposé, sans sélection de famille par une heuristique linguistique.
Les refus ne passent jamais par une nouvelle prose Luna. U-P montre le plan
développé et U-C protège les actes lourds selon leurs effets.

| Axe | Critères de décision proposés, à mesurer dans les futurs lots |
|---|---|
| I | Sur les mêmes 30 positions historiques : au moins 22 admissions au premier coup, au moins 23 intentions entières fidèles au premier coup et 27 finales selon la grille du 311, **aucune famille fidèle perdue**, au plus un abandon. Compter séparément les refus moteur exacts et les défauts de compilation/revue. Zéro substitution de cible, clause, attente, prix ou modalité dans les cas obligatoires. Aucun nouveau refus dû au contrat du compilateur ; un refus légitime nouveau exige sa contre-épreuve et reste visible. |
| V | Un appel nominal de compilation ; au plus 3,30 appels bloquants/tour sur le même corpus pour le raccord initial, sans gain obtenu par abandon. Mesurer corrections, revues et audits séparément, jetons d'entrée/préfixe, médiane/p95 saisie→rendu complet et confirmation→effet. Aucune cible de réduction de jetons avant les seuils I. Les secondes cachées ne sont pas un objectif comparatif. |
| F | Zéro suppression des demandes actuellement admises ; état, cible et reprise après recharge pour un détail et un autre support, qualification compatible et incompatible, recherche non substituée à création. Les six scripts n'en donnent pas le dénominateur : compléter les oracles de `atelier`, `assemblage`, `materiaux` et invention ciblée avant de déclarer cet axe validé. |
| P | Avis/adresse collective, ressources, dû, part contre pièces et question ouverte conservés ; prix consulté sans engagement/paiement, puis vraie contre-offre chiffrée et acceptation distinctes. Zéro parole de Corvus inventée pour une question au MJ. Mots entendus, verdict, ressources et engagements retrouvés après recharge ; un refus commercial fidèle compte comme interaction servie. |

Ces seuils sont un minimum historique, pas une précision universelle ni un
taux garanti en population. Le prix doit réellement exercer sa voie typée :
le seul affichage de 20 via `propos` ne satisfait pas ce critère. Toute perte
sur un cas obligatoire bloque le lot, même si une autre famille gagne.

Découpage proposé, **un invariant par lot**, 30–45 minutes ; pas un brief
unique portant toute la table :

1. **A0 — oracle de sens.** Le même classement distingue proposition fidèle,
   admission, exécution/refus, attente de consentement et texte réellement vu.
   Figer les références et les attentes de famille depuis les fils ; ne pas
   rejouer la référence pour chaque lot. Pas de changement de jeu.
2. **A1 — provenance publique.** Toute donnée omise possède un équivalent
   public avec provenance conservée. Rappel/texte connu et autre support,
   souvenir hors de vue et faux souvenir ; aucune réduction sémantique de
   conversation dans ce lot. Projection et tests ciblés, pas de changement
   simultané de revue ou de schéma d'action.
3. **A2 — registre d'une famille.** Une opération et ses raccourcis ont un
   sens unique pour moteur, schéma et plan public. Porter **une famille à la
   fois** ; séquence/attente, expression/son, passage et consultation sociale
   sont des lots successifs, chacun avec cas réel/autre cas/faux pendant.
   Les invariants de mécanique ne changent pas pour s'adapter au banc.
4. **A3 — liaison du transport.** Mode et charge, puis opération et paramètres,
   sont corrélés par la grammaire commune ; aucun champ voisin simplement
   légal ne peut remplacer la charge requise. Transport local/cloud de même
   sens (G3 si nécessaire), pas de sélection de schéma par lieu ou mot-clé.
   L'ordre exact dépend des limites des fournisseurs et se vérifie hors ligne
   avant une passe ciblée ; cela ne garantit pas le choix sémantique de Luna.
5. **A4 — dossier de revue.** La revue reçoit le plan développé et le sens
   proposé, y compris les clauses transitoires et la manière demandée,
   indépendamment de l'admission. Aucun retrait d'audit dans ce lot. Un refus
   fidèle et une omission réelle servent de contre-épreuves opposées.
6. **A5 — reprise fidèle.** Une correction revient à la saisie entière et au
   refus typé ; le candidat précédent reste explicitement non admis. Aucun
   texte proposé ne devient un fait moteur. Borne inchangée ; cible absente
   et autre référence, refus réel et fausse impossibilité.
7. **A6 — raccord libre.** Changer seulement le compilateur en gardant les
   garanties précédentes, U-P/U-C et les voies transitoires. Une passe ciblée
   et cas réels/autres cas après recharge. La compaction supplémentaire est
   un futur lot d'équivalence, jamais une correction de gameplay mêlée au raccord.

A2 ne consiste pas à empiler quatre familles dans 45 minutes ; la répétition
de son invariant fournit les briefs séparés. Si l'un des suivants déborde,
le superviseur le découpe avant ouverture. Aucun lot n'essaie d'achever
G12–G20 ou la nouvelle mécanique sociale dans le portage du compilateur.

### B — Compilateur des seules intentions résiduelles après interfaces

**Périmètre cible : compositions ouvertes, négociation formulée, contenu
social inédit et admissions que les U-* ne couvriront pas raisonnablement.**
Les gestes usuels ont leurs actions directes. Leurs formulations libres
restent disponibles sur la voie actuelle non portée, avec ses contrôles.
Ce n'est pas une autorisation de les refuser, ni un repli caché après échec
du nouveau compilateur.

Cette forme exige une frontière de voies explicite et stable avant d'être
codée. Un classifieur sur les mots « attendre », « avis », « sous » ou sur le
scénario déplacerait le problème de fidélité vers le routage. Si la saisie
libre unique ne permet pas de distinguer la voie sans seconde interprétation,
**B n'est pas prête** : conserver le chemin actuel pour cette entrée. Ne pas
ajouter un mode spécial pour faire passer les exemples ratés. Un éventuel
choix d'interface doit être justifié par un usage de jeu et décidé séparément.

| Axe | Critères propres à B, en plus des clauses communes de A |
|---|---|
| I | Matrice exhaustive ancien libre/direct/nouveau libre, sans intention perdue ni doublon exécuté. Les seuils 23/30 et 27/30 restent publiés sur l'ensemble historique ; publier séparément le sous-ensemble résiduel figé avant mesure. Aucun succès obtenu en retirant les tours ratés du dénominateur. |
| V | Zéro compilation/revue pour les choix U-* ; un nominal pour le résiduel, coût de routage inclus. Comparer le coût total par intention et le nombre de gestes/clics, pas seulement les appels du nouveau sous-ensemble. |
| F | Même capacité d'admission et de reprise que A ; l'interface ne doit pas obliger le joueur à répéter l'intention ou connaître le vocabulaire du moteur. |
| P | Les menus sociaux ne sont acquis qu'une fois portés ; consultation, offre, accord et parole ouverte gardent chacun leur mesure de résultat. Aucune richesse créditée au seul bouton « parler ». |

Lots : **B0**, matrice stable de couverture et provenance de chaque entrée ;
**B1**, frontière de routage sans réinterprétation d'un choix structuré ni
perte du libre actuel ; puis les lots **A1 à A5** sur le seul périmètre
résiduel, un invariant/famille par lot ; **B2**, raccord et mesure conjointe
des trois voies. B ne dispense donc pas des travaux de sens qui ont manqué
à A. Son gain de contexte reste une hypothèse, pas une mesure des archives.

## 6. Recommandation et ordre de reprise

**Choisir A comme cible ; suspendre le G1 compact actuel.** B promet surtout
de déplacer les erreurs de compilation vers un routage encore indéfini.
Les menus fusionnés ne retirent précisément pas levier, passage,
attente/vol ou question au MJ du banc G1. Attendre toutes les interfaces
sociales ne suffit donc pas à corriger ces pertes. À l'inverse, rétablir un
contexte public conservateur évite de traiter la taille comme un objectif
de gameplay et garde le texte libre disponible selon le contrat adopté.

Ordre proposé au superviseur, **non appliqué par cette note** :

1. Garder la branche 294/296/304/311 non fusionnée ; pas de « G1 e » et pas
   de retrait des contrôles d'une voie non portée.
2. Préparer A0 et les lots U-P puis U-C depuis les plans existants. Lever
   leur dépendance exclusive à G1 dans un brief d'interface : le sens et les
   effets typés existent déjà sur la voie actuelle. U-P doit notamment
   développer les raccourcis et montrer attente, cibles et termes ; U-C
   revalide l'ensemble avant les effets lourds. Si un effet n'est pas
   descriptible, le lot de son contrat précède U-C pour cette voie.
3. Reprendre A1, les lots A2 par famille, A3–A5, puis A6. Conserver les gains
   d'accès U-* déjà livrés, sans les compter comme gains de fidélité de Luna.
   Les portages G5/G15–G19 peuvent être découpés sur leurs voies existantes
   quand le superviseur confirme leurs vrais prérequis ; ne pas les regrouper
   dans G1 pour obtenir un meilleur nombre d'appels.

U-P/U-C ne prouvent pas que le joueur détectera toute omission : leur mesure
de détection réelle reste à faire, aucune revue ne se retire sur cette seule
conception. Une passe future ciblée par lot, référence exacte réutilisée,
oracles gelés avant résultat ; pas de campagne répétée pour améliorer un taux.
Tout cas réel est accompagné d'un autre cas de même nature et d'un faux
pendant, avec monde complet, texte visible et plan après recharge. La
garantie universelle de fidélité du français libre demeure hors de portée.

## Annexe — les 61 saisies sans modèle

Pour chacune, **294 = 296 = 304 = 311 : zéro appel de compilation, revue ou
génération**. Aucun petit contexte n'est donc en cause. Cela ne signifie ni
réussite de l'action ni égalité de tous les états : les tours précédents
ont pu changer temps, PNJ ou mémoire. Les refus d'identité, de portée et
les annulations restent des résultats, sans les créditer comme succès Luna.
Les textes des quatre variantes sont conservés dans `saisies.json`.

| Tour | Saisie | Voie ou résultat local (illustration 311) |
|---|---|---|
| `crypte/0` | regarder | Consultation de panneau. |
| `crypte/2` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/3` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/4` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/5` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/6` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/7` | examiner gravure | La gravure du chevalier en chêne. Un chevalier agenouillé tend une clé à une silhouette couronnée. Inscription : « Au veilleur revient le dernier serment. ». |
| `crypte/11` | annuler | Annulation locale ; ne prouve pas qu’un plan fidèle était en attente. |
| `crypte/12` | sud | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/13` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/14` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/15` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/16` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/17` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/18` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/19` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/20` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/21` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/22` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/27` | annuler | Annulation locale ; ne prouve pas qu’un plan fidèle était en attente. |
| `crypte/28` | acheter pied-de-biche | Tu te tournes vers le sud-est. |
| `crypte/29` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/30` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/31` | sud | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/32` | sud | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/33` | sud | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/34` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/35` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/36` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/37` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/38` | est | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/39` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `crypte/40` | retirer axe supérieur avec pied-de-biche | 1d20(13) + FOR(+1) + outil(+3) = 17 contre 12 : REUSSITE |
| `echanges/0` | regarder | Consultation de panneau. |
| `echanges/4` | je chuchote à Brune que je me méfie d'Aubin | Tu ne connais personne du nom de Brune ici. À la cantonade (« à tous : … »), qui t'entend retiendra tes mots. |
| `echanges/5` | Brune, laisse-moi passer s'il te plaît | Tu ne connais personne du nom de Brune ici. À la cantonade (« à tous : … »), qui t'entend retiendra tes mots. |
| `echanges/6` | je pousse Aubin | Tu ne sais pas lequel d'entre eux est Aubin. |
| `echanges/7` | je donne le bloc de cire à Ilse | Tu ne sais pas lequel d'entre eux est Ilse. |
| `echanges/8` | Ilse, qu'est-ce que tu vas en faire ? | Tu ne connais personne du nom d'Ilse ici. À la cantonade (« à tous : … »), qui t'entend retiendra tes mots. |
| `echanges/9` | inventaire | Consultation de panneau. |
| `relais/0` | regarder | Consultation de panneau. |
| `relais/3` | examiner consigne | La consigne émaillée en fer émaillé. Elle est fixée sur la face ouest de la cloison de pierre. Un croissant gravé derrière un épaulement de pierre, une petite clé et une cloche. Inscription : « Le veilleur cachait la clé au pied de l'épaulement fissuré. On ne la voit qu'en contournant le mur par son ouverture basse. La porte étanche mène au beffroi. ». |
| `relais/6` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/7` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/8` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/9` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/10` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/11` | nord | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/12` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/13` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/14` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `relais/15` | regarder | Consultation de panneau. |
| `relais/16` | Gorm, tu peux me décrire le beffroi ? | Tu ne connais personne du nom de Gorm ici. À la cantonade (« à tous : … »), qui t'entend retiendra tes mots. |
| `relais/17` | de quelle couleur sont les yeux de Gorm ? | Tu ne sais pas lequel d'entre eux est Gorm. |
| `relais/18` | Gorm, pourquoi tiens-tu tant à cette cloche ? | Tu ne connais personne du nom de Gorm ici. À la cantonade (« à tous : … »), qui t'entend retiendra tes mots. |
| `soir-appel/0` | j'appelle Gorm | Tu appelles : « Gorm ? » |
| `soir-appel/1` | je réponds | Tu réponds : « Ici, viens ! » |
| `soir-appel/6` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `soir-appel/7` | ouest | Déplacement local ; événements et éventuels obstacles dans les bruts. |
| `soir-appel/8` | je donne le briquet à Ilse | Tu ne vois pas Ilse d'ici. |
| `soir-appel/9` | Ilse, tu m'entends ? | Tu ne vois pas Ilse d'ici : approche-toi pour lui parler. À la cantonade (« à tous : … »), qui t'entend retiendra tes mots. |
