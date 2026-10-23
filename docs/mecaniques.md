# Mécaniques du prototype

Ce document décrit les mécaniques jouables et leurs limites. Le contrat entre le MJ et le
monde est décrit dans [contrat-mj.md](contrat-mj.md) ; la connexion au modèle dans
[connexion.md](connexion.md).

### Reconnaître quelqu'un et apprendre son nom

Voir quelqu'un te permet de le reconnaître de vue, sans connaître son nom. Le jeu le désigne
par son apparence : « l'homme trapu », « la femme ronde ». Tu peux employer ces mots pour lui
parler ou lui donner un objet. La carte, le terminal et la page affichent la même désignation.
Demande-lui comment il s'appelle, ou écoute quelqu'un le nommer : si tu saisis les mots et peux
les relier à lui, son nom reste appris après rechargement. Reconnaître sa voix ne suffit pas.
Les PNJ suivent la même règle pour Corvus et les autres ; seuls les liens antérieurs déclarés
par le scénario donnent un nom d'avance.

### Le corps blessable (4a)

Tous les personnages ont des PV : 6 + leur FOR de base, sauf maximum déclaré par le scénario.
Le joueur lit ses PV sur sa fiche. Les PV des PNJ restent cachés ; on voit seulement s'ils sont
blessés (au plus deux tiers des PV), grièvement blessés (au plus un tiers), ou à terre sans
connaissance. Les blessures coûtent 2 aux jets de FOR et DEX ; une blessure grave coûte encore
2 à ces jets et 2 à INT, PER et VOL. Ces malus s'ajoutent à ceux des besoins.

Une heure de repos rend 1 PV, avec les fractions de repos conservées après sauvegarde. Attendre
repose le joueur ; un PNJ se soigne pendant ses gestes de repos. Une chute à 0 PV met hors de
combat sans tuer : le joueur perd connaissance, le monde continue pendant 30 + d20 minutes,
puis il revient à lui à 1 PV dans la même action. Il ne reçoit aucun récit de ce qui s'est passé
pendant son absence ; il voit la scène à son réveil. Un inconscient reste sur sa case mais ne
voit, n'entend, n'agit ni ne parle. Son corps continue de vivre.

`ranimer <personnage>` le secoue au contact pendant 10 secondes, après au moins une minute
d'inconscience. Un protecteur qui sait son protégé à terre peut le rejoindre pour le ranimer.
La réanimation ne rend pas de PV au-delà du point nécessaire pour sortir du hors de combat.

La mort n'est encore accessible qu'aux épreuves du moteur : aucun geste de violence n'est ajouté
en 4a. Le mort devient une dépouille à la même place ; ses biens restent les siens. Les témoins
la découvrent par la vue, s'en inquiètent et peuvent transmettre la nouvelle, sans inventer de
coupable. Une partie où le joueur est mort est sauvegardée close et se recharge close.
Le banc accepte `--etat ilse:inconscient`, `--etat aubin:mort` et `--etat brune:blesse:5`.

### Le coup et assommer (4b)

`frapper` vise aussi une personne au contact. L'outil est une arme portée, ou vide pour les
mains nues ; la méthode est `simple` ou `assommer`, la difficulté 0. La fiche annonce le jet,
le risque et la durée avant « tenter ». Le même geste s'exécute chez les PNJ.

Un outil de percussion ou levier est contondant, de coupe tranchant ; un autre objet intact
d'au moins 0,5 kg est un contondant improvisé de puissance 1. Les mains nues ont puissance 0.
Le jet oppose d20 + FOR modulée à d20 + DEX modulée, égalité à la victime. Une lame de moins
de 0,5 kg emploie la DEX de l'attaquant. Si la victime ne voit pas l'auteur au début du coup,
sa défense vaut 10. Sans défense, ou tenue par un autre, elle est touchée sans jet.

Le coup dure 1,5 seconde, plus la rotation vers la cible. Il inflige 1 + puissance // 3 + mod
FOR positif, +1 pour une lame, +2 sur 20 naturel. Touchée, la victime interrompt son geste ;
consciente, elle crie (portée 9). Le coup lui-même est bruyant (7). À 0 PV, elle reste vivante,
hors de combat ; le réveil suit la règle de 4a.

Assommer exige un contondant et ôte 1 PV. Touchée par surprise ou sans défense, la victime
perd connaissance ; sinon elle résiste par d20 + VOL contre 10 + les dégâts du coup normal.
L'inconscience dure 5 + d20 minutes. La victime ne retient l'auteur que si elle le percevait ;
son réveil ne lui apprend pas qui l'a frappée. Les témoins voient ou entendent par les règles
communes, et leurs épreuves de violence passent par les relations graduées.

Un PNJ peut envisager d'assommer le porteur d'un moyen utile à son but, puis le prendre.
Le coût compte la douceur (gravité 2, avant le plafond d'enjeu), l'honnêteté séparément,
la chance et le courage. Les coûts se comparent à demander. L'approche est feutrée, par une
étape `dans_le_dos`, et se revalide sur place ; les autres témoins crus font attendre, sauf
au désespoir. Un porteur cru inconscient ne compte plus comme observateur. La douceur 100
exclut cette agression ; la fonction de prix prévoit la défense future, sans but de défense
à cette étape. Pas encore de riposte, fuite, reddition, liens ni action `tuer`.

`jeu.py --rixe` et `banc_pnj --scenario rixe` chargent l'épreuve dérivée du Relais par données ;
`--scenario rixe_douce` offre le contrôle à douceur 100. Le récit, les mesures et le rejeu
conservent les coups et les états du corps. Voir le [rapport 4b](taches/rapport-codex-12-force-4b.md)
pour les mesures et réserves de validation.

### Défi du Relais des crues et déplacement en cases

Double-cliquer sur **`lancer-defi.cmd`** pour une nouvelle scène avec **Luna seul**.
**`lancer-defi-hors-ligne.cmd`** lance exactement le même défi sans aucun appel au LLM.
Retrouver la cloche d'alarme du relais et la rapporter au refuge : un indice, des recoins
à explorer et plusieurs accès permettent de choisir son itinéraire. Ce scénario ne
déclare pas de compte à rebours : on peut prendre le temps de réfléchir.

La partie du défi est enregistrée séparément dans `sauvegardes/defi.json` et reprend au
prochain lancement. Pour recommencer : `lancer-defi.cmd --new` (l'ancienne sauvegarde
est conservée dans un fichier `.bak`). Le donjon et l'atelier gardent leurs sauvegardes.

- **Ctrl + flèches** : avancer d'une case, même pendant la saisie d'une commande.
- **F6**, puis **flèches** : piloter depuis la carte ; **Échap** ou **Entrée** revient à la commande.
- `nord`, `sud`, `est`, `ouest` ou `pas est` : mêmes déplacements dans la console.
- `examiner plaque`, `prendre clé`, `ouvrir porte avec clé`, `installer échelle contre rebord`,
  `monter échelle`, `descendre échelle` : exemples de commandes locales. `aide` donne la liste.
- Les prises simples comme `je ramasse le pied de biche` ou `je prends la clé` sont aussi
  exécutées localement, avec les mêmes contrôles de portée et de propriété. Les demandes
  conditionnelles, discrètes ou combinées restent confiées au MJ.
- `sonner <objet>` utilise un objet sonore à portée ; une source lumineuse créée par le MJ
  s'allume avec les mêmes règles de combustible et d'allumage qu'une lanterne du scénario.
- `couper <cible> avec <outil>` entaille une cible si une règle de coupe du scénario
  accepte cet outil ou si le MJ a fait valider leur compatibilité. Le moteur fixe les
  dégâts et la cible est sectionnée lorsque son intégrité tombe à zéro. Pour une cible
  encore inconnue, Luna juge l'outil employé sans inventer un seuil chiffré global ;
  la même demande est reprise après validation et sauvegarde.
- Une capacité physique peut être inconnue, établie ou écartée dans les conditions
  constatées. Luna peut établir qu'un objet observable résiste à l'outil de coupe
  employé, peut être entamé par lui, ne sonne pas ou ne peut pas éclairer. Le moteur conserve le constat avec
  l'état physique de l'objet et celui de l'outil évalué. Après rechargement, ce même
  outil dans le même état reste sans effet ; un autre moyen ou un changement physique
  de l'un des deux ouvre un nouvel arbitrage sans effacer ce qui a été établi.
- Les objets doivent être sur la même case ou une case voisine pour être manipulés.
  Il faut s'approcher pour lire les petits détails ; les murs, les portes et les obstacles
  opaques bloquent la vue. Les objets pris quittent immédiatement la carte.

La carte garde le terrain exploré et distingue ce qui est visible maintenant. Dans la TUI,
les cases visibles sont vert sombre et les cases explorées hors de vue bleu ardoise ; une
légère alternance de teinte laisse compter les pas. La console conserve `.` pour le terrain
visible et `:` pour le terrain mémorisé.
Les murs sont des blocs `##`, y compris dans les angles. `+` désigne uniquement une porte
fermée, `X` une porte verrouillée et `/` une porte ouverte dans ce mode.
Une consigne ou un objet fixé à un mur occupe la case du mur sur la carte : son symbole
remplace le premier caractère du bloc (`!#` par exemple). La case de sol voisine reste
son point de manipulation. Hors de vue, le symbole mémorisé reste sur le mur (`!~` dans
la console, symbole grisé sur le mur dans la TUI) jusqu'à une nouvelle observation.
Seuls les murs effectivement aperçus sont mémorisés. Une case parcourue dans le noir ne
révèle pas à elle seule les murs voisins ; les murs déjà vus restent dessinés. Les dimensions
d'une pièce n'apparaissent qu'une fois tout son sol exploré.
Les lieux encore inconnus restent blancs. Les niveaux explorés restent affichés ensemble ;
une échelle installée porte le même repère `H1` à ses deux extrémités. Un objet déjà vu
hors du champ de vision garde son symbole à sa dernière position observée, en gris bleuté
dans la TUI. Ce souvenir peut être périmé : il s'efface si la case est revue vide ou si le
joueur prend l'objet. La console sans couleur préfixe les souvenirs au sol par `~` ;
sur un mur, elle place `~` après le symbole. Une case représente un mètre,
affiché sur deux colonnes pour conserver des proportions lisibles dans le terminal.
Le dernier état vu d'une porte reste également indiqué hors de vue, avec la même couleur
de souvenir. Il peut avoir changé depuis ; la carte l'actualise quand le seuil est revu.
Dans le noir, la case que Corvus vient de fouler reste connue : sa position et l'escalier
emprunté demeurent sur le niveau d'arrivée, sans révéler le reste de la pièce.

Un pas en avant dure 1,5 s ; un pas chassé (de côté ou en arrière, sans se tourner) ou feutré,
3 s ; se tourner de 45°, 0,5 s. Un pas en diagonale dure √2 fois un pas droit, à toute allure,
arrondi au dixième de seconde le plus proche (2,1 s, 4,2 s), pour le joueur comme pour les PNJ
(`temps.duree_pas`) : un trajet en diagonale n'est plus plus rapide qu'en vrai. Les chemins (la
marche des PNJ, `spatial.trajet` ; le clic sur la carte) sont les plus courts en temps, pas en
nombre de pas. On ne coupe pas l'angle d'un mur ou d'un obstacle en diagonale. Toute portée en
cases (lumière, vue, ouïe, voix) se mesure en distance réelle, arrondie à la case la plus proche
(`geometrie.distance`) : une case voisine, même en diagonale, est au contact (1) ; deux cases en
diagonale sont à 3, quatre à 6. Les portées dessinent des disques, pas des carrés. Le temps
consomme le combustible minute par minute. Franchir un seuil
ou un escalier est une transition vers la première case de l'autre côté. La lumière, la ligne
de vue et les obstacles sont calculés case par case (voir « Lumière en cases » plus bas).
Les touches de déplacement, les collisions, la visibilité et les commandes locales sont
entièrement déterministes et ne consomment aucun appel au LLM. Le MJ reçoit les objets
perceptibles et leur portée, puis le moteur vérifie aussi ses propositions d'action.
Les objectifs de chaque partie sont déclarés dans son état ; le moteur n'exige pas les
objets de la crypte pour résoudre une action. La crypte, le Relais et l'atelier possèdent
chacun leur état initial dans `donjon/scenario_*.json`. Le Relais et l'atelier démarrent
sans construire la crypte ; l'atelier ne contient que sa cour, sa terrasse et son matériel.
`nouveau_monde_libre` crée aussi une aventure à partir de ses
propres salles, objets, départ, prémisse et objectif. Le contrat de narration et de paroles
des PNJ est décrit dans
[docs/contrat-mj.md](docs/contrat-mj.md).
Le corpus de contre revue et ses résultats sont décrits dans
[docs/evaluation-portee-narrative.md](docs/evaluation-portee-narrative.md).

Les lanceurs du donjon et de l'atelier activent également ce mode. En ligne de commande :

```powershell
.\.venv\Scripts\python.exe jeu.py --defi --tui --offline
.\.venv\Scripts\python.exe jeu.py --atelier --cases --tui --model gpt-6-luna
```

### Atelier : premier harnais de fabrication

Double-cliquer sur **`lancer-atelier.cmd`** pour tester avec **Luna seul**, ou lancer :

```powershell
.\.venv\Scripts\python.exe jeu.py --atelier --tui --debug --model gpt-6-luna
```

Cette scène utilise `sauvegardes/atelier.json` ; la partie principale reste dans `partie.json`.
Elle contient trois perches de 3 m, une bobine de ficelle, une hache et une terrasse à 2,4 m.
En mode cases, rapproche-toi des matériaux et rassemble-les à portée avant de fabriquer ;
transporte ensuite l'échelle près du mur pour l'installer. `fabriquer échelle` est aussi
une commande locale, qui choisit le travail soigné lorsque les conditions le permettent.
Exemple de parcours :

1. « Avec ces perches et la ficelle, est-ce que je peux fabriquer une échelle ? »
2. « Je prends mon temps pour fabriquer soigneusement cette échelle » : 52 minutes, sans jet.
3. « Je la pose contre le mur ».
4. « Je monte à l'échelle », puis **tenter**.
5. « Je redescends par l'échelle », puis **tenter**.

La fabrication prélève les matériaux, conserve les restes et crée un objet persistant.
Les pertes de coupe et la quantité de lien sont contrôlées. En fabrication normale (26 minutes,
jet et confirmation **tenter**), un échec dépense du temps et deux mètres de lien, sans créer
d'échelle. Le travail soigné double la durée et supprime le jet dans un lieu établi comme calme,
avec assez de lumière pendant toute la durée et sans urgence plus proche. Il respecte les mêmes
contraintes de matériaux et d'outils ; il ne rembourse pas les pertes des essais précédents.
La cour de l'atelier autorise ce travail au calme, y compris pour une partie déjà sauvegardée.
Sans préférence ni urgence, le MJ privilégie le travail soigné. La difficulté normale est mémorisée pour un
assemblage comparable. Les dimensions, appuis et charges conditionnent l'installation et
le franchissement. `désinstaller échelle`, depuis son pied, supprime cet accès.
Les plans des étages sont affichés séparément. Lors de l'utilisation d'une échelle installée,
un échec laisse le personnage de son côté, sans chute simulée.

#### Franchissement improvisé avec un appui mobile

L'objectif de l'atelier est d'atteindre la terrasse par la méthode choisie par le joueur.
L'échelle est une possibilité, pas une solution obligatoire. « Je prends une perche et
je tente un saut à la perche pour franchir le mur » devient une manœuvre composée : prise,
puis `franchir_obstacle` avec la méthode `appui_mobile`. Luna estime une difficulté de DEX
entre 16 et 22 ; le moteur mémorise cet arbitrage pour des conditions comparables.

Ce premier cadre de JDR exige un appui intact assez long et solide, un élan établi d'au moins
3 m, un sol et une réception stables, et une hauteur au plus de 3 m. Ce ne sont pas des calculs
de mécanique réelle. La scène d'atelier établit 4 m d'élan et un palier stable, y compris au
chargement des anciennes parties d'atelier ; les propriétés déjà renseignées restent prioritaires.
Les autres lieux doivent fournir leurs propres propriétés : le MJ n'invente pas une réception.

La prise et le saut sont proposés ensemble avant confirmation. Sur réussite, le joueur arrive
sur le palier ; sur échec, il reste au pied et subit une blessure proportionnée à la hauteur
(3 PV dans l'atelier). Un 1 naturel endommage aussi l'appui. Celui-ci est lâché au pied dans
les deux cas ; aucun accès permanent ou retour automatique n'est créé. Le modèle de chute
est une conséquence forfaitaire de JDR, sans trajectoire détaillée.

Le dossier `franchissements` présente les conditions vérifiées et les obstacles/inconnues.
Un refus initial du MJ est réexaminé une fois avant de conclure à une impossibilité,
sans forcer une réussite ni contourner un obstacle réel. `tools/test_saut_reel.py` vérifie la
phrase avec Luna seul, puis résout réussite et échec sur des copies en mémoire.

Le harnais fournit à Luna un dossier calculé localement : ressources, mesures manquantes,
proposition réalisable si disponible, consommation et durée. Les intentions de fabrication
reçoivent le dossier atelier et ses règles lorsque le joueur demande une action. Une proposition
invalide reçoit son obstacle et **un seul essai de correction**, sans effet sur le monde avant
résolution. Si la correction échoue, Luna peut expliquer les conditions attestées sans raconter
une tentative de Corvus. Une question ne déclenche pas de fabrication.
Les commandes connues restent locales ; aucun second modèle ni modèle de secours n'est lancé.

« Je retente » ou « je réessaie » reprend la dernière tentative échouée sans appel
d'interprétation au LLM : même méthode, ressources revalidées, étapes déjà réussies exclues.
Une tentative risquée attend toujours **tenter**. Pour changer de méthode après un échec,
préciser par exemple « Cette fois je prends mon temps pour fabriquer soigneusement l'échelle ».
Le moteur raconte ensuite les conséquences, comme pour les autres actions.
Le contexte du MJ contient aussi la dernière tentative résolue et les quantités exactes de lien
disponibles/requises, pour éviter les clarifications inutiles et les fausses annonces de pénurie.

`F5` en mode debug montre les réponses, propositions, usages et refus de validation de Luna.
Les traces sont aussi enregistrées dans `artifacts/mj/`, sans clés ni jetons. Les informations
techniques restent hors de la chronique. Une action valide demande un appel d'interprétation ;
une correction ou une réponse libre peut ajouter des appels de contrôle.

**Portée actuelle :** un premier profil d'assemblage à barreaux. Ce n'est pas encore un
générateur universel de recettes, de lieux ou de lois physiques. Les charges sont des valeurs
de jeu établies dans la scène, pas calculées depuis le diamètre du bois. Une mesure inconnue
reste à établir ; le LLM n'est pas autorisé à inventer silencieusement une résistance.
Les propriétés et usages sont disponibles dans toute partie qui contient les ressources
et appuis correspondants ; l'atelier est une scène d'essai, pas une modification de la partie existante.

Validation réelle : `python tools/test_atelier_reel.py` vérifie les cinq intentions ci-dessus
avec Luna seul et des jets fixés pour parcourir toutes les étapes, sans lire ni écrire la
sauvegarde utilisateur. Les tests unitaires couvrent aussi les échecs, le rechargement et les
propositions corrigées. La prose et les initiatives hors de ce parcours restent à éprouver.

Modèle conservé avec effort `medium`, compatible avec Responses et les appels de fonction :
[OpenAI Docs — GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).

### Jouer

#### Détails du personnage joueur

Corvus est explicitement un **humain adulte**. Ce socle est présent dans l'état du monde,
la fiche et le contexte du MJ ; il est ajouté au chargement des anciennes parties sans
écraser une identité déjà renseignée. Les compléments doivent rester cohérents avec cette
espèce, le stade de vie, le poids et les traits connus.

Le MJ peut préciser la couleur des yeux, celle des cheveux et la corpulence dans le même
mécanisme persistant que l'âge et la taille. Un portrait complète les traits visuels utiles,
sans inventer d'équipement, de pouvoirs, de passé personnel ni de bonus de caractéristiques.

Les questions « je mesure combien ? » et « je fais combien de haut, moi ? » concernent
la taille corporelle de Corvus, même après une discussion sur un dénivelé. Une taille ou
un âge absent peut être proposé par Luna avec `enrichir_joueur`, validé puis sauvegardé
avant d'être annoncé. Le complément ne change ni les caractéristiques ni le temps de jeu.
Il apparaît dans la fiche et n'est pas régénéré aux questions suivantes.

Le cadre actuel est celui d'un aventurier adulte : taille 140–210 cm, âge 18–90 ans.
Seul le détail demandé est complété ; les valeurs déjà établies restent prioritaires.
Le poids, s'il est connu, vient de `masse_kg`, distinct du poids de la besace.
La réponse initiale est formulée localement après validation : pas de second appel de narration.

#### Improviser une action hors du catalogue

Le MJ dispose d'un arbitrage sommaire `improviser` : intention, cibles, outil, durée,
bruit, éventuel jet et deux issues conditionnelles. S'étirer ou fredonner ne demandent
pas de règle dédiée ni de jet. Une proposition « impossible » est réexaminée une fois
avec le même modèle. Le schéma est disponible dès le premier appel : aucun second modèle.
Luna propose les effets des deux issues ; le moteur raconte le geste et les effets de la
branche effectivement résolue. Son brouillon libre n'est ni affiché ni conservé comme fait.
Avant l'exécution, une contre-revue compare la demande entière aux opérations validées
par le moteur. Si une conséquence perceptible manque, Luna reçoit l'écart et peut corriger
le plan une fois ; aucune action n'a lieu tant que le plan n'est pas accepté.

La résolution est validée sur une copie puis appliquée et journalisée par le moteur.
Les gestes passés reviennent dans le contexte sous forme structurée (approche, cibles,
outil, résultat), sans reprendre l'intention ou le récit rédigés par Luna. Une marque
devient un détail réel,
examinable sur son support et conservé dans la sauvegarde. Les sons laissent un souvenir
aux PNJ à portée avec une forme acoustique bornée (voix, souffle ou rythme corporel),
sans transformer une proposition libre de Luna en parole entendue. Les mouvements
d'objets réutilisent les contrôles de propriété,
d'accessibilité, de poids et d'attaches. Les blessures de cet arbitrage sont limitées
à 3 PV au total et ne peuvent tuer ; blessures et usure exigent une tentative confirmée.
Une difficulté est mémorisée pour la même intention et les mêmes conditions pertinentes.

Exemples : « je m'étire », « je fredonne une chanson », « je grave une flèche sur la perche
avec mon couteau », « je jongle avec la clé ». Une chute d'objet n'est racontée que si
la branche résolue déplace réellement cet objet. Les tests réels sont dans
`tools/test_improvisation_reel.py` et n'utilisent aucune sauvegarde du joueur.

Le moteur valide les effets structurés et produit le résultat affiché. La formulation
de l'intention proposée par Luna reste dans les données d'arbitrage ; l'aperçu et le
résultat affichés emploient des formulations du moteur.
L'improvisation ne remplace pas la géométrie pour un franchissement, les règles de fabrication
pour un nouvel objet fonctionnel, ni les mécanismes de dialogue pour un engagement de PNJ.

#### Abords, déplacements d'échelle et sauts

La terrasse possède des bords explicites : retour vers la cour au sud, murs latéraux,
et un cadre de génération au nord. À la première interaction avec le MJ depuis la terrasse,
Luna complète ce cadre par un terrain (terre, pierre ou herbe). Le moteur calcule une surface
rectangulaire adjacente, ses coordonnées, son dénivelé et son appui ; il refuse chevauchements,
doublons et modifications des faits existants. Les abords sont enregistrés avant la réponse
ou l'action. Cette complétion utilise un appel supplémentaire une seule fois, visible dans
le debug sous « complément spatial ». Une observation locale hors ligne ne génère pas de lieu.

« J'attrape mon échelle pour la remonter sur la terrasse, puis je la mets de l'autre côté
pour en descendre » peut produire une seule manœuvre composée : `soulever`, `appuyer`,
`franchir`. Le moteur vérifie masse, propriété, prises, stabilité, longueur et charge.
Un assemblage installé reste accessible depuis ses deux extrémités ; le retirer le dépose
du côté du personnage et supprime l'ancien passage. L'installation depuis le haut est possible.

`sauter` utilise un bord et son sol de réception établis. Le jet de DEX décide de l'amorti,
pas de l'existence de la chute : réussite et échec déplacent le personnage en contrebas,
avec des blessures différentes annoncées avant confirmation (2 ou 5 PV pour 2,4 m).
Il s'agit de règles de JDR, sans simulation balistique. La carte indique les bords et l'échelle
sans afficher les surfaces voisines non visitées.

Les anciennes parties d'atelier reçoivent le cadre au chargement, sans perdre leur progression.
`tools/test_terrasse_reel.py` rejoue les trois demandes avec Luna sur une partie en mémoire.
La génération reste bornée aux cadres déclarés par l'auteur : elle ne crée pas encore
librement villes, bâtiments ou recettes. Le terrain choisi ne change pas les dégâts de chute
dans cette première version.

#### Appeler, crier et siffler

`je crie à l'aide`, `crier au secours`, `crier` et `siffler` fonctionnent aussi hors ligne,
sans appel au modèle ni jet de dés. Les formulations libres passent par Luna avec l'opération
composable `emettre_son`. Un son coûte une minute et augmente le bruit.

L'audition est l'ouïe commune (`donjon/ouie.py`, `docs/plan-ouie.md`), la même que pour les pas,
les gestes et les voix : un appel à l'aide ou un cri porte comme un appel (9 crans), un sifflement
comme un fracas (7), le son d'un objet selon sa sonorité (`ouie.SONS` : 1 un geste, 2 un fracas, 3
un appel, la cloche d'alarme) ; la distance en cases, chaque ouverture (un cran) et chaque porte
fermée (trois) l'atténuent, les paliers reliés par un appui vertical le transmettent. Qui l'entend
sans voir le joueur en retient un bruit vers ce lieu (le dernier est fourni au dialogue, sans
révéler l'identité des PNJ hors de sa perception) et s'en inquiète à la mesure de ce qui lui
parvient ; un appel porte la voix, que reconnaît qui la connaît. Luna n'affirme ni réponse ni
arrivée que l'état n'établit pas : un PNJ va voir par sa délibération (son devoir de garde, son
courage, ou son seuil d'alerte, `profil["alerte"]`, en crans : un bruit qui lui parvient à ce niveau
l'envoie voir avant tout le reste ; le protecteur qui reconnaît l'appel de son protégé accourt de
même), exécutée par le moteur (voir « Perception et croyances des PNJ »). Son arrivée dans la
perception du joueur est annoncée par le moteur (`donjon/pnj.py`).
Sans réaction perceptible, la restitution est :
« Tu cries à l'aide. Pour l'instant, aucune réponse ne te parvient. »

Héler quelqu'un par son nom (`j'appelle Gorm`, `je crie « Gorm ? »`) est un cri du moteur, par la
règle des PNJ (`docs/plan-ouie.md`, « L'appel négocié ») : l'appelé qui en saisit les mots convient
avec l'appelant de qui vient à qui. Il répond « J'arrive ! » (il vient : il cherche lui-même
l'appelant, on le prie de venir, ou ce qu'on lui veut le regarde ou se trouve sur lui), « Ici, viens ! »
(il ne peut ou ne veut bouger : un geste en cours sur place, une garde, ce qu'il fait sur place, un
passage qu'il croit fermé, ce qui le presse ailleurs) ou « Qu'est-ce que tu veux ? » (libre, sans raison
de bouger) ; il se tait s'il se méfie de cette voix ou prépare un geste qu'il veut sans témoin. Le
joueur l'entend par l'ouïe commune et répond sans le MJ : `j'arrive`, `viens` (ou `je réponds`,
`« Ici ! »`), et, à un appel par son nom, `qu'est-ce que tu veux ?` ; le PNJ y donne suite par la même
règle (« J'arrive ! » s'il peut venir, ce qu'il veut, « Ici, viens ! » s'il ne le peut pas). Qui reste
attend le temps que l'autre met à venir par le plus court chemin, et sa moitié, plus deux minutes ;
« J'arrive ! » est une parole donnée : attendu en vain jusqu'à l'échéance, celui qui l'a dite — joueur
compris — n'est plus tenu pour fiable par qui l'attendait.

#### Attendre

`attendre` fait passer cinq minutes ; `attendre 30 s`, `attendre 10 min`, `attendre 1 h 30` (sans
unité, des minutes) une durée choisie, jusqu'à douze heures, sans appel au modèle. Dans la page et
dans le terminal, Espace sur une saisie vide (ou la carte) fait attendre le temps d'un pas (1,5 s) ;
dès qu'un caractère est tapé, Espace redevient une espace. Le temps passe par tranches de 15 s
(`Moteur._attendre`), ce qui donne le même monde qu'un bloc ; le joueur cesse d'attendre à la fin
de la tranche où il a vu, même un instant, quelqu'un qu'il ne voyait pas, ou entendu un appel, un
cri, un fracas ou des paroles dont il saisit les mots (`ecoute.eveille`) ; des pas, un geste
ordinaire, des voix dont les mots lui échappent ne l'interrompent pas. Il lit « Tu attends
10 minutes. » ou « Au bout de 2 minutes 15 secondes, tu cesses d'attendre. », puis ce qu'il a
entendu et le bilan des présences. Attendre repose et fait retomber le bruit (trois crans par cinq
minutes). Le MJ propose `attendre` avec la cible vide (cinq minutes d'un bloc, sans interruption,
comme le banc) ou une durée en secondes.

#### Perception et croyances des PNJ

Chaque PNJ perçoit avec les règles du joueur, depuis sa propre case : lumière par case,
ligne de vue, obstacles opaques, portes (`donjon/esprits.py`). La ligne de vue est
symétrique : elle exige que le tracé passe dans les deux sens, si bien que deux personnages
se voient mutuellement ou pas du tout, à éclairage égal. L'asymétrie vient de la lumière :
un joueur dans la pénombre voit de loin un PNJ éclairé sans être vu de lui. Sans cases, un
PNJ perçoit sa salle si elle est éclairée. Il sait ce qu'il porte ; chez autrui, il ne
remarque que les objets encombrants (1 kg ou 50 cm au moins) ou allumés.

Ce qu'il perçoit devient croyance dans `esprits[pnj]["croyances"][sujet][attribut]`, avec
`source` (`vu`, `savoir`, `essai`), `minute` et `confiance`. Attributs : `lieu` (avec la salle
et la case où il l'a vu), `etat` (ouvert, allumé ; d'un personnage, joueur compris, ce qui presse
son corps : `faim`, `chaleur`, `repos`), `verrouillee` (appris en essayant, ou
déduit d'une porte vue ouverte). Une croyance reste vraie pour lui tant qu'il n'a pas revu
la place : s'il la revoit vide, le lieu devient inconnu et la mémoire note une `absence`.
Un scénario déclare les savoirs initiaux dans les mêmes champs, source `savoir` (le Relais :
Gorm croit la cloche dans la galerie, la clé au refuge et la porte étanche verrouillée).
La mémoire (40 événements) garde les sons entendus, les absences constatées, les vols
surpris et les gestes remarqués.

#### Besoins, pulsions et plans des PNJ

Un PNJ peut porter un `profil` d'auteur (`donjon/deliberation.py`) : `caracteristiques`
(FOR, DEX, INT, PER, CHA, VOL, ELO, PSY), `traits` (prose destinée à Luna), `valeurs`
(altruisme, empathie, honnêteté, douceur, ambition, courage, loyauté, fierté, de 0 à 100 ;
voir « Caractéristiques et valeurs »), `capacites` (`crochetage`), `besoins` (`devoir`, `biens`, `securite`,
`faim`, `repos`, `chaleur`, chacun avec `depart`, `derive_heure`, `urgence`) et `pulsions` : des
conditions sur le monde (`{"objet", "lieu"}`, `{"objet", "verrouillee": true}` ou un feu
entretenu `{"objet", "allume": true}`) liées à un besoin, éventuellement `delegue_a` le
joueur, ou des rondes (`{"lieu", "periode"}` : avoir inspecté ce lieu depuis moins de
`periode` minutes).

Chaque minute écoulée, le moteur fait dériver les besoins. Une pulsion qui cesse d'être
satisfaite *selon les croyances du PNJ* est rompue, quelle qu'en soit la cause : il la rétablit
sans attendre que son besoin presse (voir l'ordre ci-dessous), et elle le reste jusqu'à ce
qu'il la voie rétablie. Une pulsion qui n'a jamais été satisfaite depuis qu'il la connaît (un
désir, comme le voleur qui convoite un ballot) attend que son besoin presse. Une atteinte
relance en outre le besoin de 30, de 60 s'il s'agit de ses biens (un vol découvert, même sans
coupable) ; une ronde qui expire, un feu qui baisse ou un protégé qui a faim ne relancent
rien. Un vol vu par sa victime relance ses biens de 60 ; l'absence constatée d'un
objet qui lui appartient, de 30.

Le PNJ retient le premier but pour lequel il trouve un plan, dans cet ordre :
1. Ce qui presse vraiment, du besoin urgent (valeur ≥ urgence) le plus en dépassement au moins
   pressant :
   - manger pour la faim. Il mange d'abord ce qui est à lui ou à personne. Sinon, il demande une
     part au propriétaire des vivres : il va là où il le croit, ou, s'il en a perdu la trace, le
     cherche dans la salle qu'il a parcourue le moins récemment, celle où il se tient comprise.
     Une part promise s'attend près des vivres, 60 minutes au plus. Sinon, si son honnêteté le
     permet, il prend le bien d'autrui ; un plan qui lèse quelqu'un peut aussi l'emporter sur une
     longue démarche honnête, selon le prix de la faute ;
   - se reposer là où il est pour le repos (2 points par minute, jusqu'à 20) ;
   - se mettre à l'abri pour la sécurité : rejoindre une salle qu'il croit éclairée où se tient
     quelqu'un qu'il croit fiable, là où il est d'abord, et y rester jusqu'à 30 ; ses rondes
     restent des recours ;
   - pour la chaleur, se chauffer près d'un foyer qu'il croit allumé (3 points par minute,
     jusqu'à 20). Sans feu vif, il ranime un foyer qu'il croit éteint, avec les recours de la
     faim : son bois ou celui de personne, puis une part de bois demandée au propriétaire, puis,
     si son honnêteté le permet, le bois d'autrui. Une part de bois acceptée est l'engagement
     d'entretenir ce feu : le donneur va lui-même le recharger et l'allumer ;
   - rétablir une pulsion.
2. Ses engagements.
3. Rétablir une pulsion rompue dont le besoin ne presse pas : un feu qui baisse, un protégé
   qui a faim, ce qu'il garde sous clé et a lui-même ouvert, ce qu'il a lui-même emporté. Les
   rondes ont leur routine (5), et une pulsion confiée au joueur attend.
4. Finir de se reposer ou de se chauffer.
5. La routine : ses rondes et la garde du lieu de ses biens. Les rondes se font aussi quand le
   besoin qu'elles servent ne presse pas ; elles passent après tout le reste.

Le corps est commun à tous, joueur compris (`donjon/corps.py`) : la faim monte de 6 par heure,
la fatigue de 3, le froid de 4 au sec et de 10 trempé ; l'effort (marcher, porter, agir)
multiplie faim et fatigue par 1,5 ; dans la salle d'un foyer allumé, le froid baisse de 3 par
minute et l'on sèche en 30 minutes ; attendre repose ; se tourner sur place ne creuse pas.
Seuils : 70 (faim, froid), 80 (fatigue). Le corps vit le temps réellement passé dans chaque état
(l'effort ou le repos du geste fait, le chaud d'un feu, l'eau) : traverser une salle chauffée
ou noire en quelques secondes compte ces secondes, pas une minute (`donjon/vecu.py`).
Le scénario déclare des états (`corps` : minutes depuis le dernier repas, de veille, trempé),
dont découlent les valeurs de départ ; le profil d'un PNJ ne règle plus le corps. Pour le
joueur comme pour les PNJ, un état qui presse coûte 2 aux jets de FOR et de DEX, et la fatigue
aussi à ceux d'INT et de PER (« Caractéristiques et valeurs ») ; à 95, la faim ou le froid ôtent
1 PV par heure, jamais en deçà de 1 ; `manger <nourriture>` (cinq minutes) mange une part de ce
qui est à lui ou à personne. Il peut demander une part de vivres (servie là où ils sont) ou de
bois (le feu entretenu) à qui les possède, même sans les avoir vus.

Tout geste fait un bruit, du joueur comme d'un PNJ (`donjon/ouie.py`, `docs/plan-ouie.md`) : pas
feutré (1) < pas, geste ordinaire (3) < voix (4) < geste bruyant (7 : crocheter, forcer, frapper…)
< appel, cri (9). Un cran se perd par distance doublée (en distance réelle) dans une salle, un en passant une ouverture,
trois une porte fermée. Chacun entend ce qui lui parvient au niveau 1 ; le joueur, en écoutant
(`ecouter`, trois minutes), un cran plus bas, et un de mieux contre la porte par où le bruit
arrive (`donjon/ecoute.py`). Une parole n'est rendue en clair qu'au niveau 1 et si elle ne nomme
que ce qu'il connaît. Un PNJ saisit les mots d'une parole à la même condition (niveau 1, un cran
de plus au repos) : il la retient, qu'elle lui soit adressée ou non, et ce qu'elle transmet le
touche comme son destinataire (une affirmation se juge comme une confidence, une nouvelle comme
une rumeur, un aveu se croit) ; plus loin ou derrière une porte, il n'entend qu'une voix. Un
chuchotement est feutré (1) et ses mots ne vont qu'à son destinataire. Un PNJ interprète le bruit selon ce qu'il croit : celui de qui il croit là
ne le fait pas se retourner ; un bruit inconnu ou inhabituel, si, de près ; de plus loin, il s'en
inquiète, et son devoir de garde ou, pour un fracas ou un appel, son courage l'envoie voir. Le
joueur lit qui se retourne vers lui.

Un PNJ protège ceux que déclare son profil (`protege`) : à bout d'inquiétude et sans abri, un
protégé appelle à l'aide, et son protecteur accourt ; un geste illicite vu contre un protégé
relance le devoir du protecteur, qui va prévenir la victime.

La sécurité suit ce que le PNJ perçoit, minute par minute, en plus de sa dérive : le noir sur
sa case (+0,5) et la vue de quelqu'un qu'il ne croit pas fiable (+0,3) l'inquiètent, la lumière
(−0,2) et la vue, dans sa salle, de quelqu'un qu'il croit fiable, le joueur compris (−0,5), le
rassurent. D'un coup : un bruit fort venu d'une autre salle (+15), un geste illicite vu (+20),
une ronde accomplie (−20). Ces valeurs par défaut (`SECURITE`) se nuancent par profil, donnée
`securite`. Un PNJ sait si la salle où il se tient est éclairée (croyance d'état `eclairee`
sur la salle), même sans en voir la source.

Un plan qui accède à un contenant qu'il garde sous clé se termine en le refermant. Ce qu'il
défait lui-même pour un plan qui le rétablit n'est pas à réparer d'abord, tant que le motif
du plan presse encore : Gorm qui déverrouille sa réserve pour servir une part ne la
reverrouille pas avant d'avoir servi. Il ne s'alarme pas de ce qu'il vient de défaire
lui-même (sa clé, sa main) : ce n'est pas une atteinte. Une pulsion déléguée au joueur
attend tant que le PNJ croit le joueur fiable. Un but abandonné n'est repris qu'après 60
minutes. Un besoin qui vient à peine de devenir urgent (moins de 5 points au-delà de son seuil,
`INERTIE`) n'interrompt pas le plan en cours d'un autre motif : on achève le geste entamé.

Une part se demande pour toute ressource comptée qui répond à un besoin du demandeur : des
vivres (`portions`) pour la faim, un combustible (`charges`) pour le froid ou pour un feu qu'il
entretient ; on ne demande pas ce qu'on a sur soi. Le propriétaire garde `reserve` parts
(donnée de profil, 1 par défaut) et ne donne pas ce dont il a lui-même besoin ; il ne prête pas
davantage une ressource comptée qu'il porte (prêter ce qui se consomme, c'est en donner les
parts). Une part promise s'attend 60 minutes ; une part de bois est servie dès que le
demandeur a revu, depuis la promesse, le feu rechargé. Une parole donnée n'est tenue que sur ce
que le PNJ a constaté depuis qu'il l'a donnée : un feu vu vif avant qu'on lui demande d'y mettre
du bois, il va le revoir ; une part à servir ne l'est qu'au geste.

Servir un protégé (pulsion `{"objet", "servir"}`) ne se fait que si le serveur le croit
affamé (sa faim presse, et cela se voit) ; il le voit manger la part servie, et s'arrête là.

Un feu entretenu (pulsion `allume`) se juge sur ce que le PNJ en voit : le feu qui baisse se
voit 45 minutes avant de s'éteindre, et un foyer froid montre s'il lui reste du combustible.
Un feu vu vif il y a plus de 30 minutes, ou jamais vu, doit être revu : il va le voir. Vu
baisser, il va chercher un combustible qu'il peut prendre et le recharge, ou en demande une
part à qui en possède (le donneur vient lui-même recharger et rallumer ce feu) ; éteint, il le
recharge s'il est vide puis l'allume s'il trouve de quoi l'allumer, sinon il n'y touche pas.
De quoi allumer : un outil d'allumage, une source qu'il croit allumée et peut prendre, ou une
source éteinte et chargée qu'il va allumer à une flamme fixe (la torche au fanal) ; une source
fixe ne se déplace pas. Une flamme se voit de loin, même dans le noir : une source crue
allumée, sous son regard, qui ne brille pas, est crue éteinte ; un feu vu baisser s'est
consumé, un feu vu vif garde le combustible qu'il lui supposait. Il connaît l'état qu'il laisse
de ses mains à un objet, même sans le voir. Une flamme portable allumée ou employée pour
allumer, que son plan n'emploie plus, est éteinte et gardée.

Le plan est cherché sur les croyances, jamais sur la vérité, par décomposition bornée
(profondeur 4) : obtenir un objet, accéder à un contenant (l'ouvrir, le déverrouiller avec
une clé connue ou le crocheter si le PNJ en a la capacité et l'outil), aller dans une salle
(une porte crue verrouillée fait chercher sa clé). Les objets fixes sont connus de lieu ;
les autres ne le sont que par croyance. Un geste sur le bien d'autrui est interdit à
l'honnêteté 100 ; sinon il coûte le prix d'une faute et porte la garde `sans_temoin`. Le plan est recalculé chaque minute.

Exécution : un geste par minute (aller d'une salle, s'approcher au contact, prendre, poser,
ouvrir, fermer, déverrouiller, verrouiller, crocheter, manger, alimenter un foyer avec un
combustible porté, l'allumer avec un outil d'allumage ou une autre flamme (l'une des deux
portée), éteindre, se chauffer dans la salle d'un foyer
allumé, inspecter : gagner la case libre la plus proche du centre de la salle pour la
parcourir des yeux, ce qui accomplit la ronde), revalidé sur l'état réel ;
un échec corrige la croyance qui l'avait motivé. Crocheter est un jet de DEX du PNJ contre
14 + 4 par niveau de lumière manquant, comme pour le joueur. Une étape `sans_temoin` attend
que le PNJ ne perçoive plus personne depuis la case de son geste ; au-delà de 30 minutes, il
renonce. Un besoin à 95 ou plus l'emporte sur cette crainte : le PNJ agit sous les yeux de
tous. Les témoins réels sont ceux qui le perçoivent pendant la minute du geste, y compris
ceux qui arrivent avant qu'elle s'achève : un PNJ témoin d'un geste illicite (une tentative
de crochetage ratée comprise) s'en souvient, cesse de croire l'auteur fiable et, s'il en
est la victime, voit ses biens relancés. Le moteur annonce au joueur ce qu'il perçoit et tient une `chronique` complète
(300 entrées), réservée au débogage.

Le réflexe déclaré `reaction_son` n'existe plus : le seuil d'alerte du profil fait aller voir par la
délibération, avant tout le reste (`deliberation.alarme`).

Le Relais déclare Gorm (honnête, devoir de rapporter la cloche délégué au joueur, d'entretenir
le brasero de l'échoppe et de faire ses rondes au refuge et aux vannes, réserve de vivres
sous clé), Brune, batelière évacuée, affamée et capable de crocheter, Ilse, meunière bavarde
qui va et vient entre le refuge et le brasero, et Aubin, vieux passeur qui surveille l'eau
aux vannes. Les trois évacués sont trempés : leur besoin de chaleur monte de 10 par heure.
Tous ont faim avant la fin de la nuit, et la réserve ne compte que 4 parts ; Gorm garde la
dernière pour lui. Le brasero brûle 150 minutes ; deux charges de fagots, rangés aux vannes
et qui sont à Gorm, l'entretiennent chacune 120 minutes de plus, et les planches de bac
d'Aubin, au refuge, deux charges de 90 minutes. La torche du refuge attend éteinte, avec 60
minutes de combustible : elle porte la flamme du fanal jusqu'au brasero. Les trois évacués, voisins, se croient fiables entre eux. Les évacués savent Gorm à
l'échoppe, le brasero allumé et les vivres dans la réserve ; Gorm les sait au refuge et les
tient pour fiables. Un fanal éclaire le refuge pendant douze heures. Le banc `python -m donjon.banc_pnj --heures 8 --joueur chambre_cloche` fait
vivre le scénario sans joueur actif et imprime chronique et mesures (gestes, événements
distincts hors routine, échanges, minutes de besoin urgent sans intention, renoncements,
gestes illicites vus, confidences, rumeurs crues ou doutées, méfiances), sans appel à Luna
sauf avec `--stratege` ; `--graine` choisit les jets, `--sortie` écrit un JSON. Le banc A/B
`python tools/banc_stratege.py` compare les deux sur plusieurs graines.

Les témoins d'un geste discret du joueur sont les personnages qui le perçoivent au moment
du geste. En `--debug`, `esprit <personnage>` affiche croyances, mémoire et intention.

#### Vie sociale des PNJ

Les PNJ se confient ce qu'ils savent (`donjon/social.py`). Une nouvelle est un souvenir :
geste illicite vu (`vu_agir`), vol surpris, bien aperçu aux mains d'un autre (`vu_porter`),
mensonge découvert ou démenti, objet disparu, ou rumeur reçue. Un PNJ désœuvré, ou qui
guette une occasion sous des yeux, consacre sa minute à confier une nouvelle à un
personnage de sa salle qu'il perçoit et qui le perçoit, à qui il ne refuse pas sa confiance.
Il ne la confie ni à celui qu'elle accuse, ni à celui qui la lui a apprise, ni deux fois au
même ; un objet disparu ne se dit qu'à son propriétaire déclaré ; il ne répète que ce qu'il
croit encore. Ce qu'il sait d'un même accusé se dit d'un coup, en une confidence.

L'auditeur l'adopte avec la règle des paroles du joueur : une disparition démentie par ce
qu'il a vu dans les 30 dernières minutes est rejetée et il cesse de croire le locuteur
fiable ; sinon, jet de persuasion du locuteur contre 10, avec les mêmes modificateurs de
confiance. Crue, l'accusation devient `fiable` faux (source `dit:<locuteur>`) ; la victime
voit ses biens relancés de 30. La confiance vaut 0,7 (0,35 pour une INT ≤ 8), multipliée
par 0,8 à chaque relais ; une rumeur de troisième main n'est plus répétée. Une croyance
`dit:` contredite plus de 30 minutes après avoir été dite est seulement périmée : le monde a
pu changer, ce n'est pas un mensonge.

Le propriétaire qui voit son bien porté par un autre (joueur compris), sans le lui avoir
prêté, découvre un vol : il cesse de le croire fiable et ses biens sont relancés de 60. La
méfiance d'un PNJ envers le joueur, vue ou rapportée, renforce sa vigilance contre un geste
discret et le fait paraître méfiant.

Le joueur entend ce qui se dit dans sa salle : « Ilse glisse à Gorm que Brune a mangé une
part des vivres du refuge. » si Corvus connaît chacun de ceux dont on parle, sinon un échange
à voix basse ; d'une autre salle, il voit seulement deux personnages parler. Arrivées et
départs sont annoncés à la minute où ils se produisent. Luna reçoit les croyances des
personnages présents avec leur source (« Ilse le lui a dit ») si Corvus connaît ce témoin.

#### Caractéristiques et valeurs

Tout personnage, joueur compris, a huit caractéristiques (`donjon/caractere.py`) : FOR, DEX,
INT, PER, CHA, et VOL (volonté), ELO (éloquence), PSY (perspicacité) ; 10 quand rien ne les
déclare (anciennes parties, joueur). Les états les modulent, par la même règle pour tous
(`corps.malus`) : chaque état qui presse coûte 2 points de jet aux caractéristiques qu'il
touche (faim et froid : FOR, DEX ; fatigue : FOR, DEX, INT, PER), et la volonté brisée
(`corps["volonte_brisee"]`, 0 à 5 points, qu'aucune contrainte n'entame encore) en ôte à la
VOL. Toute règle lit la valeur modulée : crochetage d'un PNJ (DEX), INT de ce qu'on retient,
vigilance d'un témoin contre un geste discret (PER), dégâts du joueur (FOR). Le jet de
persuasion (croire une affirmation, accepter une demande ou une tâche) est d20 + CHA + ELO du
locuteur contre un DD que la confiance règle et que la VOL de l'auditeur élève. PSY n'est
encore employée par aucune règle.

Les valeurs d'un PNJ (0 à 100) sont des poids, stables. Une valeur à 100 interdit : honnêteté
100, ni voler ni mentir ; douceur 100, ni blesser ni pousser (pousser et frapper sont des gestes de
contrainte du moteur, voir « Laisser passer, demander le passage, pousser »).
Les anciennes limites deviennent ces valeurs à leur comble au chargement (`ne_vole_pas` et
`ne_ment_pas` : honnêteté 100 ; `ne_blesse_pas` : douceur 100), les autres valeurs à 50.

- **Honnêteté** : léser une personne (prendre, ouvrir, manger son bien) coûte au plan
  20 × h / (100 − h) minutes, compté une fois par personne lésée. La détresse du besoin servi
  (0 au seuil d'urgence, 1 à 100) l'use jusqu'à 90 %, d'autant moins que la VOL est haute
  (usure = détresse × 10 / VOL). Une faute qui coûterait plus de 60 minutes n'est pas
  envisagée : à 90, on ne vole qu'à bout ; à 20, on se sert plutôt que de traverser le relais
  pour demander.
- **Douceur** : pousser quelqu'un est une faute au même prix, calculé sur la douceur ; une
  douceur de 75 ou moins l'envisage sans détresse, 90 seulement à bout.
- **Altruisme** : le DD d'une demande (objet prêté, part de vivres ou de bois) baisse d'un
  point par dizaine au-dessus de 50 chez celui qui donne, monte en dessous.
- Les valeurs vont au stratège et au MJ avec les traits (le MJ ne fait mentir un personnage
  que si son honnêteté le permet). La fierté, avec l'altruisme, décide si l'on s'écarte de
  soi-même pour laisser passer. Empathie et courage ne pèsent encore sur aucune règle du
  moteur ; ambition, altruisme et loyauté font aussi le prix d'une pièce (ci-dessous).

#### Prêter, confier, payer

Les mêmes règles valent pour le joueur et pour les PNJ (`donjon/biens.py`).

- **Prêt** : un objet qui dure, remis par son propriétaire (demande acceptée, geste `remettre`),
  est prêté (`data["permissions"]`) : l'emprunteur le prend, le pose, l'allume, le recharge sans
  faute ; une clé prêtée ouvre, ferme et verrouille ce qu'elle ouvre, pas plus (le contenu reste
  au propriétaire). Le prêt est clos quand l'objet revient entre les mains de son propriétaire,
  de quelque façon que ce soit. Un PNJ emprunteur s'engage à le rendre (`{"objet", "rendre"}`) :
  il le rapporte quand il ne lui sert plus (ni son plan, ni une pulsion, ni la lumière dont il a
  besoin) ; le propriétaire qui le redemande le récupère sans jet, sauf s'il sert encore. On ne
  demande un objet qu'à son propriétaire (ou ce qui est à soi).
- **Don** : ce qui se consomme (une part, du bois) ne se prête pas, il se donne : remis par son
  propriétaire, il change de propriétaire.
- **Garde confiée** : une tâche acceptée sur un bien de celui qui la confie (garder la réserve
  sous clé) permet au délégué d'agir sans faute sur ce bien et sur les clés de son propriétaire
  qui l'ouvrent, tant que dure la tâche ; ce qu'il en porte encore à la fin lui reste prêté, et
  il le rend. Une pulsion déléguée au joueur (`delegue_a`) lui confie de même la garde de son
  objet.
- Aucune permission ne couvre ce qui consomme le bien d'autrui : le manger, en servir une part.
- **Argent** : le joueur a son or ; chaque PNJ une bourse (`data["finances_pnj"]`, 5 pièces
  quand le scénario n'en déclare pas). Un objet peut contenir des pièces (`pieces` : une bourse,
  une paie) : qui le porte peut les dépenser. Une part d'une ressource comptée a un prix
  (`prix_part`, 2 sinon), un objet le sien s'il en déclare un (`prix`).
- **Ce que vaut une pièce** pour un PNJ, en minutes de plan (`caractere.valeur_piece`) :
  (10 + ce qui lui manque hors de la scène) / (10 + ce qu'il peut dépenser), au plus 6. Ce qui
  lui manque : 5 pièces pour vivre une fois sorti, sa dette, 10 par proche à charge (pesés par
  son altruisme et sa loyauté), son projet (pesé par son ambition), déclarés dans
  `profil["situation"]`. Une somme vaut la suite de ses pièces à mesure qu'il s'enrichit
  (`valeur_pieces`) : la deux-centième vaut moins que la première.
- **Acheter** : payer le prix au propriétaire est un achat, qu'il accepte sans jet s'il ne garde
  pas ce bien (sa réserve, son besoin, ce qui sert son plan) et ne se méfie pas de l'acheteur ;
  l'acheteur paie aussitôt, la part promise est servie comme une part donnée. Moins que le prix,
  c'est une demande : pour ce qui se consomme (qu'il perd), le DD monte d'un point par 2 minutes
  de ce que vaut pour lui la part du prix qu'on ne lui paie pas, au-delà de ce qu'elle vaut à qui
  vit modestement (un riche donne plus volontiers, un endetté rechigne) ; un objet qui dure se
  prête, sans ce surcoût. Un PNJ demande d'abord, puis achète s'il peut payer et
  si le prix lui coûte moins que l'autre voie (une faute, une longue démarche).
- **Prendre des pièces** : des pièces qu'il connaît et qui ne sont pas à lui, il va les prendre
  si elles valent pour lui plus que ce qu'il lui en coûte (le chemin, la faute à son prix), sans
  que rien ne presse ; c'est son dernier but, après la routine. Une dette rend la paie plus
  tentante ; l'honnêteté 100 l'interdit.
- **Le joueur paie** dans une parole : une demande (`valeur` : les pièces offertes) ou une
  demande de passage (`valeur` : les pièces offertes à qui ne s'écarterait que par orgueil ; ce
  qu'elles valent pour lui abaisse le DD, il ne les prend que s'il s'écarte). Offrir plus que son
  or est refusé au MJ avec un `attendu`. Payée son prix, la part est vendue : « Gorm prend tes 2
  pièces et accepte de t'en donner une part » ; moins, Gorm dit son prix s'il refuse. Une part de
  combustible achetée sans qu'aucun feu soit nommé est un bien qu'on achète (`echanges._vendre_part`) :
  le vendeur en détache une part (une pièce du lot s'il la décrit, sinon une réserve d'une charge) et
  la remet à l'acheteur, aussitôt s'il la porte, sinon quand il est allé la chercher (« Aubin prend tes
  3 pièces et ira chercher une part des planches de bac pour te la remettre ») ; non remise à
  l'échéance, le prix est dû. Seule une part demandée pour un feu (sans payer, ou par un PNJ qui
  entretient ce feu) va au feu. Une part de vivres reste servie.
- **« As-tu du bois ? »** : on répond par ce qu'on croit avoir, et l'on sait ce qu'on porte et ce qui
  est à soi à portée de main, dans sa salle hors de tout contenant fermé (`echanges.siens_a_portee`),
  même sans l'avoir regardé.
- **Une contrepartie payée et jamais livrée** (`biens.rembourser`, `solder`) : une part vendue
  d'avance, un objet acheté que le vendeur ne portait pas (il s'engage à l'aller chercher et à le
  remettre, `echanges.differee`), une tâche payée. À l'échéance de la parole (240 minutes), ou
  dès qu'il ne peut plus la tenir (ce qu'il vendait est épuisé, perdu, n'est plus à lui), le
  vendeur doit le prix. La dette (`data["dettes"]`, sa nature `quoi` : part, objet, tâche) est
  connue des deux. Quand ils se retrouvent, le débiteur rend ce qu'il peut, s'il le veut ; le reste
  demeure dû. Le joueur le lit (« Gorm te rend 7 pièces : le marteau que tu avais payé ne t'a pas
  été remis. ») ; un PNJ créancier va réclamer son dû quand il vaut pour lui plus que le chemin
  (but `reclamer`, après la routine), et ne relance pas de sitôt un débiteur retrouvé sans le sou.
- **Rendre est un choix** (`biens.garde_du`) : garder l'argent dû est une faute au prix de son
  honnêteté (comme prendre des pièces, sans usure par la détresse), contre ce que valent pour lui
  ces pièces. À l'honnêteté entière on rend toujours ; Brune (honnêteté 20, endettée) garde 2
  pièces, Lucien (50) en garde 4, Joss (50) rend la sienne. Le débiteur qui garde ne dit rien ;
  réclamé, il refuse : le créancier cesse de le croire fiable et peut le confier comme une nouvelle
  (« Brune garde les 2 pièces qu'elle doit à Ilse »), qu'on adopte comme une rumeur. Il ne lui
  redemande pas avant 120 minutes.
- **Le joueur réclame** dans une parole (contenu `reclamer` : sujet vide pour les pièces qu'on lui
  doit, ou un objet à lui que l'autre porte) ; le moteur tranche : « Gorm te rend 2 pièces… »,
  « Brune refuse de te rendre les 2 pièces qu'elle te doit. », « … ne te doit rien. » ; un sujet que
  le moteur ne sait résoudre est refusé au MJ avec un `attendu`. La fiche (`fiche`, `inventaire`)
  montre ses comptes : ce qu'on lui doit, ce qu'on lui a prêté (`biens.comptes_joueur`).
- **Le prêt réclamé** : passé l'échéance (240 minutes), le prêteur va redemander son objet à qui
  le garde, PNJ ou joueur (but `reclamer`), comme il le redemande quand il en a besoin. Un PNJ
  emprunteur qui s'en sert encore refuse ; le joueur lit « Gaspard te demande de lui rendre la
  lampe… » et décide. L'emprunteur qui garde un prêt échu qu'on lui réclame (le PNJ qui refuse, le
  joueur qui ne l'a pas rendu 30 minutes après) perd la confiance du prêteur, qui peut le dire.
- **Tâche payée entre PNJ** (`echanges.engager`, geste `engager` du planificateur) : pour une de
  ses pulsions (un feu à entretenir, un bien sous clé, un objet à remettre en place) sur ce qu'il
  pourrait faire lui-même sans faute, un PNJ peut offrir des pièces à qui se tient avec lui, une
  par 3 minutes de la peine qu'il estime (le chemin et 5 minutes de travail) ; dans son plan, cela
  coûte la demande, ses pièces et l'attente de cette peine. L'autre accepte, sans jet, si ces
  pièces valent pour lui au moins ce que la tâche lui coûterait (un feu, il le compte à recharger),
  sauf méfiance, s'il n'y emploie pas ce qu'il garde, et refuse sinon (« cher », « impossible »,
  « necessaire »). Acceptée, elle devient son engagement, payé d'avance, et lui confie la garde du
  bien ; le payeur ne la fait pas à sa place tant qu'elle court. Non faite à l'échéance, le prix
  est dû (ci-dessus).
- **Demander ce qu'on ne connaît pas** (`echanges.enqueter`) : « as-tu du bois ? », « de quoi
  manger ? ». Quand rien de ce qu'il connaît n'apaise sa faim, son froid ou le feu qu'il entretient,
  un PNJ le demande à qui il ne connaît rien de tel (le plus proche, une fois par 120 minutes).
  L'autre répond par ce qu'il a vraiment (ses ressources comptées pour ce besoin, qu'il croit avoir
  encore, et où), sauf méfiance ; le demandeur l'apprend par ouï-dire, et rien de plus. Le joueur
  le demande par la parole (contenu `ressource`, sujet `faim` ou `chaleur`) et lit la réponse.

#### Relations graduées

Les PNJ retiennent séparément leur confiance, leur affection, leur rancune, leur peur et leur
dette morale envers chacun, joueur compris. Les liens de départ appartiennent au scénario.
Un don, une part reçue, une parole tenue ou un avertissement peuvent regagner la confiance ;
attendre seul ne la rétablit pas. Une restitution de prêt dans les temps compte comme une
parole tenue, sans devenir un don. La dette morale ne remplace pas les pièces ou objets dus.

Une demande reste refusée d'office dans la méfiance ou avec une rancune d'au moins 60 ; sinon
la confiance, l'affection et la dette facilitent le jet, la rancune le rend plus difficile.
La méfiance commence sous 30 de confiance et ne cesse qu'à 40. La peur et la rancune
s'estompent, l'affection revient vers le lien de départ ; ces effets persistent après reprise.
Un même fait rapporté plusieurs fois ne compte qu'une fois ; le voir ensuite complète la
preuve. Les conséquences d'une promesse faite hors de vue s'apprennent par un résultat reçu
ou une annonce entendue, jamais en voyant simplement le promettant.

Rendre un objet après un vol surpris améliore la relation sans effacer le souvenir du vol.
L'interdiction de vente après un vol surpris reste distincte. Les signes visibles et la lecture
des attitudes ne sont pas encore réalisés (étape 3c).

#### Échanges entre PNJ et stratège

Un plan de PNJ peut contenir quatre gestes sociaux (`donjon/echanges.py`), d'une minute
chacun, dans la salle d'un personnage qu'il perçoit et qui le perçoit : `dire` (affirmer un
lieu, un verrou ou la fiabilité de quelqu'un, avec la règle des paroles du joueur : démenti
par ce que l'auditeur a vu récemment, sinon jet de persuasion du locuteur contre 10),
`demander` (un objet que l'autre porte : refusé s'il se méfie ou s'en sert, sinon jet contre
12, abaissé d'un point par dizaine d'altruisme au-dessus de 50 chez celui qui donne, relevé
en dessous ; un PNJ qui a faim peut aussi demander une part d'une nourriture qui appartient à
l'autre, même rangée sous clé : refusée s'il se méfie, a faim lui-même ou n'a plus qu'une
part, sinon même jet, et l'autre s'engage à venir la servir),
`confier` (faire en sorte qu'un objet soit en un lieu, ou verrouillé : refusé s'il se méfie
ou ne voit pas comment s'y prendre d'après ce qu'il croit, sinon jet contre 12) et
`remettre` (un objet porté, au contact). On s'approche de celui à qui l'on parle. Le geste
`servir` donne une part à quelqu'un de la même salle, appelé s'il est hors de vue : il la
mange et tient désormais le donneur pour fiable. Le joueur et les PNJ passent par les mêmes
fonctions ; le joueur, qui n'a pas faim, ne demande pas de part. Une tâche acceptée devient un engagement : le PNJ l'exécute avec son
planificateur quand rien d'urgent n'a de plan, et l'oublie après 240 minutes ou dès qu'il
la croit accomplie. Le joueur entend ces échanges comme les confidences.

Le stratège (`donjon/stratege.py`, option `--stratege` du jeu et du banc, désactivé par
défaut) est Luna consultée pour un PNJ dans trois cas : un besoin urgent sans plan du
moteur ; un seul plan qui touche au bien d'autrui (voler ou non dépend du caractère, sauf à
bout de besoin, à 95 ou plus, où le moteur passe outre) ; une heure désœuvré. Il reçoit les
traits, besoins, pulsions, engagements, croyances, souvenirs récents et objets que le PNJ
croit connaître, jamais la vérité du monde, et renvoie un plan typé (1 à 6 gestes),
« suivre » le plan du moteur ou « attendre » (seul « attendre » écarte le plan illicite du
moteur pour une heure ; une autre voie qui échoue le laisse revenir). Le moteur valide chaque geste : identifiants
connus du PNJ, salles, capacités, honnêteté 100 (ni le bien d'autrui, ni dire autre chose que
ce qu'il croit), demander seulement à qui il croit porter l'objet, remettre seulement ce qu'il porte
ou aura obtenu ; on ne redemande pas pendant 2 heures le même objet à qui vient de le
refuser, mais on peut lui demander autre chose. On peut confier un feu à entretenir.
Le stratège dit quoi, le moteur dit comment : le planificateur complète chaque geste de ce
qu'il suppose d'après les croyances du PNJ (aller là où il faut, ouvrir ou déverrouiller le
contenant de l'objet visé, aller chercher la clé ou les crochets) et ajoute la garde
`sans_temoin` ; un geste qu'il ne sait pas rendre possible est refusé avec sa raison. Un écart est renvoyé une
fois au stratège. Adopté, le plan devient l'intention du PNJ jusqu'à son terme ; un geste
manqué ou refusé l'abandonne. Budget : une consultation par PNJ et par heure de jeu, deux
appels par heure pour tout le scénario, correction comprise. Le joueur ne voit que les
gestes qu'il perçoit ; les buts et justifications de Luna restent dans la chronique.

#### Paroles du joueur aux PNJ

Quand le joueur fait parler Corvus à un personnage présent, Luna choisit le mode
`parole_joueur` (`donjon/paroles.py`). **À qui** : le moteur le fixe, pas Luna, d'après la
saisie (`paroles.analyser`, les formes reconnues sont des données en un seul endroit) :

- celui que le joueur nomme : en tête (« Brune, … », « à Brune : … »), après un verbe de parole
  (« je dis à Gorm que… », « je demande à la meunière… »), ou en tête des mots entre guillemets ;
- la suite de l'échange : des mots entre guillemets sans interpellation, « je lui dis… », « je
  leur dis… » s'adressent à ceux à qui Corvus a parlé en dernier, s'ils saisissent encore ses
  mots (« lui » : un seul ; « leur » : plusieurs ; les guillemets : un ou plusieurs) ; sinon la
  règle suivante ;
- sinon celui qui est en face de lui : parmi les présents qu'il perçoit et qui saisiraient ses
  mots, celui qu'il a dans son regard, le plus proche ; deux à égalité (ou, sans cases, deux
  présents), le joueur précise : « Aubin et Ilse sont aussi près de toi l'un que l'autre :
  précise à qui tu parles… » ;
- « à tous : … », « à tous, … », « je dis à tous… », et « je leur dis… » sans échange à
  plusieurs en cours : tous les présents qui
  saisiraient ses mots ; chacun décide de ce qui lui est demandé comme d'une demande
  individuelle (pas de décision collective) ;
- « je chuchote à Brune… », « je murmure… » : un seul destinataire, nommé ou en face, au contact
  (une case voisine ; sans cases, quiconque est là). Jamais à un groupe. Les mots ne vont qu'à
  lui ; le chuchotement retentit comme un bruit feutré (1).
- une parole sans conteste (guillemets, à tous, deux-points) que nul présent perçu ne saisirait
  est dite à la cantonade : aucun destinataire, personne ne répond, qui l'entend la retient.

Une saisie qui commence par des guillemets vaut « je dis … », ou « je lui/leur dis … » quand un
échange est en cours ; entre guillemets, après un
deux-points ou une interpellation, les mots du joueur sont prononcés tels quels. Une saisie
entre guillemets, à tous ou chuchotée est une parole même si ses mots annoncent un geste : le
moteur refuse une action à sa place (« « Gorm, je te donne la cloche » » reste une parole ; le
don passe par `donner`). Un nom absent, trop loin pour entendre, un chuchotement à distance ou à
plusieurs sont refusés avec un `attendu`, et le message est rendu au joueur sans relance du MJ.
Luna reçoit ce que le moteur a fixé (`parole_prevue` : personnage, destinataires, manière, mots
imposés) et doit le reprendre ; un autre personnage est refusé.

Le moteur lui fournit la bande d'expression de Corvus :
précision selon l'INT (très pauvre ≤ 7, pauvre ≤ 9, courante ≤ 12, précise ≤ 15, riche),
aisance selon le CHA (même découpage, de très maladroite à brillante). Luna écrit la réplique
dans cette bande et type son contenu, trois éléments au plus : `affirmation` (sujet, attribut
`lieu`, `verrouillee` ou `fiable`, valeur), `demande` (un objet que le personnage porte),
`passage` (qu'il s'écarte, se pousse, laisse passer : voir ci-dessous), `aveu` (un geste
illicite que Corvus avoue avoir fait sur un objet qui n'est pas à lui), `reclamer` (son dû :
les pièces qu'on lui doit, ou un objet à lui), `ressource` (« as-tu du bois ? » : `faim` ou
`chaleur`), `propos`. La réplique est
enregistrée avant l'affichage, qui commence par « Tu dis à Gorm : « … » » (« Tu dis à tous »,
« Tu chuchotes à Brune »).

**Qui l'entend.** Une parole à voix haute retentit par l'ouïe commune avec ses mots : tous ceux
qui les saisissent la retiennent (souvenir `parole` : qui parlait, à qui, ses mots), destinataires
ou non ; ce qu'elle transmet touche un témoin par la même règle que le destinataire (une
affirmation se juge comme une confidence, avec son jet ; un aveu se croit : il ne tient plus Corvus
pour fiable et le sait de première main, de quoi le confier au propriétaire comme une rumeur).
Une demande ou une prière adressée à un autre n'engage pas le témoin. Les PNJ entendent les
paroles des autres PNJ par la même règle : une confidence surprise devient une rumeur, une
affirmation entendue se juge comme si on la leur avait dite. Seuls les destinataires répondent :
le contrôle narratif refuse une parole d'un témoin (`conversation_validee.destinataires`) ;
Luna voit ce que chaque présent a entendu récemment (`a_entendu`), sauf ce qui nomme ce que le
joueur ne connaît pas.

L'effet ne dépend pas des mots de Luna. Corvus ne peut parler que de ce qu'il connaît :
entité perçue, examinée, vue auparavant ou nommée devant lui, lieu visité. Il transmet au
plus 1 idée avec une INT ≤ 9, 2 jusqu'à 12, 3 au-delà ; l'auditeur retient selon sa propre
INT, et une INT ≤ 8 diminue sa confiance dans ce qu'il retient. Une affirmation contredite
par ce que l'auditeur a vu ou essayé dans les 30 dernières minutes est rejetée sans jet et
il cesse de croire le joueur fiable. Sinon, jet de d20 + modificateurs de CHA et d'ELO contre
10 (−2 s'il croit le joueur fiable, +2 s'il n'en sait rien, +6 s'il le croit peu fiable, plus
le modificateur de VOL de l'auditeur) :
réussi, la croyance devient `dit:joueur` ; ce qu'il a sous les yeux peut la démentir
aussitôt. Une croyance `dit:` que la perception ou un essai contredit plus tard est un
`mensonge_decouvert` : il cesse de croire le locuteur fiable. Une demande d'objet réussit
contre 12 avec les mêmes modificateurs, sauf si le personnage se méfie du joueur ou si
l'objet sert son plan en cours ou une de ses pulsions.

Luna reçoit, pour les personnages présents, leurs traits, ce qu'ils croient (douze
croyances au plus, celles qu'on leur a dites d'abord), leur but actuel et leurs besoins
pressants : jamais la vérité à leur place, jamais leur profil brut. Les objets qu'un
personnage porte ne sont pas perçus par le joueur s'ils sont petits et éteints, avec la
même règle que pour les PNJ.

#### Laisser passer, demander le passage, pousser

Trois règles communes au joueur et aux PNJ (`donjon/passage.py`), en mode cases.

- **Laisser passer.** Personne ne s'arrête sur la case d'un autre. Quand quelqu'un doit
  s'arrêter sur la case d'un PNJ (un pas du joueur ; pour un PNJ, la case d'où il ouvre une
  porte, ou la seule d'où il atteint ce qu'il veut toucher), ce PNJ s'écarte de lui-même d'une
  case, le temps d'un pas de côté (3 s), puis laisse l'autre passer d'abord : vers une case
  voisine libre de sa salle, hors du
  chemin de l'autre (ni sa case, ni celle qui suit dans le sens du passage), de côté d'abord.
  Il reste s'il a une raison de rester : un geste en cours là où il se tient (ce qu'il touche
  est à portée de sa main), ou la porte qu'il s'apprête à ouvrir ; ou s'il ne veut pas aider
  ce passant : il le croit peu fiable, ou sa fierté dépasse son altruisme de 30 points ou plus
  (qui le croit fiable l'aide toujours). Garder un lieu, pour le moteur, c'est se tenir dans
  une salle : un pas de côté ne l'en fait pas sortir. Le joueur lit « Brune s'écarte pour te
  laisser passer. » puis « Tu avances d'un pas. » ; sinon le pas est refusé (« Brune se tient
  là, sur ton passage, et ne s'écarte pas. »), et le MJ reçoit la raison et ce qui reste
  possible : le lui demander ou le pousser.
- **Demander le passage.** Une demande typée (contenu `passage` d'une parole du joueur ; geste
  d'un PNJ bloqué), que le moteur tranche : refusée s'il a une raison de rester ou se méfie du
  demandeur, impossible s'il n'a pas la place ; acceptée sans jet par qui s'écarterait de
  lui-même ; l'orgueilleux se laisse convaincre par le jet de persuasion contre 8, moins un
  point par dizaine d'altruisme au-dessus de 50, plus un par dizaine de fierté. Acceptée, il
  s'écarte réellement avant la réponse du personnage, que Luna écrit d'après cette issue
  (« Brune s'écarte d'un pas pour te laisser passer. ») ; une réplique ne promet pas de bouger
  plus tard.
- **Pousser.** Un geste de 3 s au contact (action `pousser`, commande `pousser <personnage>
  [vers <direction>]`) : d20 + FOR modulée contre d20 + FOR modulée de la victime, l'égalité
  ne déplace pas. Réussi, la victime recule d'une case libre dans le sens de la poussée, jamais
  vers celui qui pousse ; sans direction, elle est écartée du chemin : de biais, de côté, droit
  devant en dernier. Réussie ou non, c'est une contrainte légère : la victime cesse de croire
  l'auteur fiable et s'en inquiète ; ceux qui voient faire pendant le geste (registre des gestes
  en cours, `vu_agir` de l'opération `pousser`) aussi, et peuvent le raconter.
- **Un PNJ bloqué** attend d'abord que l'autre s'écarte de lui-même, ou qu'il ait fini le geste
  qui le retient là ; sinon il le lui demande (une parole de 10 s, s'ils se voient), puis,
  refusé, le pousse hors de son chemin si sa
  douceur le permet (au prix de la faute, voir « Caractéristiques et valeurs ») ; sinon il
  patiente, et un but ordinaire est abandonné après 30 minutes passées à attendre (`PATIENCE`,
  compté au temps, quel que soit le nombre de fois qu'il y repense). Le
  joueur sur son passage n'est jamais déplacé d'office : il est prié de le laisser passer
  (« Gorm te demande de le laisser passer. ») ; s'il n'a pas bougé 30 s plus tard, c'est un refus,
  et un PNJ peu doux peut le pousser (« Gorm te pousse : tu recules d'un pas. »).

#### Horloges d'environnement

Un scénario peut déclarer des `horloges` : `{"id", "minute", "effets", "annonce", "lieux"}`.
Dès que les minutes de la partie atteignent l'échéance, le moteur applique les effets, une
seule fois, et l'annonce n'est montrée que si le joueur se trouve dans l'un des `lieux`.
Les effets sont ceux des transitions de scénario : `deplacer`, `objectif` et `eteindre`
(sources allumées des salles citées). Un effet devenu sans objet est ignoré
(`donjon/horloges.py`). L'auberge déclare la rafale qui éteint l'âtre.

#### Départ tiré de la graine

Un scénario déclare un état de départ ; le moteur en tire une variante à la création du monde
(`donjon/depart.py`), par un tirage à part (`random.Random(f"{seed}:depart")`) que les jets ne
décalent pas, une seule fois (minute 0), gardée dans `data["depart"]` avec les valeurs
appliquées : un rechargement ne tire plus rien. Pour chaque PNJ qui a un profil :

- les états du corps (minutes depuis le dernier repas, de veille, passées trempé), à `corps`
  près de leur valeur déclarée (écart relatif ; un état nul le reste) ;
- les besoins du profil (devoir, biens, sécurité…), à `besoins` points près ;
- chaque période de ronde, à `periodes` près (écart relatif), puis sa phase : la prochaine ronde
  tombe entre la minute 0 et `rondes` fois sa période (au départ déclaré, toutes sont dues à la
  minute 0) ;
- et l'échéance de chaque horloge, à `horloges` près (écart relatif).

Aucun tirage ne mène un besoin au-delà de 85 (sous l'extrême et le désespoir, 95), sauf si le
scénario l'y a déjà déclaré. Les bornes se déclarent dans `data["depart"]["bornes"]` ; celles
qu'un scénario ne déclare pas valent les défauts du moteur. `depart="fixe"` (constructeurs des
scénarios, `banc_pnj --depart fixe`) garde le départ déclaré.

#### Crue : le niveau d'eau

Un scénario peut déclarer une `crue` (`donjon/eau.py`) : `depart_cm` (niveau au départ) et des
bornes `[min, max]` pour `montee_cm_heure`, `heure_pic`, `hauteur_pic_cm` et, facultative,
`baisse_cm_heure`. Les valeurs sont tirées une fois de la graine, par un tirage à part
(`random.Random(f"{seed}:crue")`) que les jets ne décalent pas, et gardées dans la sauvegarde.
L'eau monte de sa montée jusqu'à l'heure du pic sans dépasser sa hauteur, puis baisse.

- Comparée à `altitude_cm`, une salle est **mouillée** dès qu'il y a de l'eau, **noyée** à
  100 cm : on n'y entre plus (pas du joueur, `aller`, échelle ou saut, chemins et trajets des
  PNJ ; on peut quitter celle où l'on est), et un feu posé que personne ne porte s'y éteint et
  ne s'y rallume pas. Une source portée reste allumée.
- Entrer ou se tenir dans l'eau trempe, joueur et PNJ ; debout dans l'eau, on ne sèche pas, même
  près d'un feu (`corps`). Le joueur lit la hauteur d'eau dans la scène et sur les sorties
  (« sous l'eau », « eau trop haute pour passer ») ; le MJ la reçoit dans `salle.eau`.
- Un PNJ sent l'eau de sa salle et voit celle des salles voisines par un passage ouvert
  (croyance `eau` de la salle). Revue quinze minutes plus tard, elle lui donne une vitesse : il
  attend l'eau là où elle arrivera dans l'heure (à tort si le pic est proche). Se tenir dans
  l'eau inquiète (2 par minute à 50 cm), l'attendre aussi (1), la voir gagner un lieu d'un coup
  (10). Un lieu où il croit ou attend l'eau n'est pas un abri ; tant qu'il voit l'eau monter,
  l'abri est le plus haut lieu éclairé qu'elle ne menace pas, avec ou sans compagnie.
- `python jeu.py --crue` (sauvegarde `crue.json`) et `python -m donjon.banc_pnj --scenario crue`
  jouent le Relais dérivé (`donjon/scenario_crue.json`) : salles basses sous le refuge, galerie
  au-dessus, brasero dans la conduite, la plus basse.

`tools/test_cri_reel.py` vérifie la phrase exacte avec Luna seul, sans sauvegarde utilisateur.

Depuis ce dossier :

```powershell
python jeu.py
```

Sous Windows, double-cliquer sur `lancer.cmd` ouvre directement la TUI. L’environnement local
`.venv` et ses dépendances sont installés dans ce projet. `python jeu.py` ouvre également la TUI
dans un terminal interactif et utilise cet environnement si Textual manque au Python courant.

L’écran contient la carte et la fiche par onglets, la scène actuelle, un journal défilant et une
zone de saisie. Après chaque commande, la carte, la scène, les ressources et la besace sont
recalculées depuis le même état du jeu. Ramasser une clé la retire immédiatement de la carte.
Les messages du journal restent consultables ; le redimensionnement replie les paragraphes.

- **F1** : aide ; **F2** : carte ; **F3** : personnage.
- **Souris** : glisser sur le texte pour le sélectionner ; **Ctrl+C** : copier la sélection.
- **F4** : copier le dernier échange complet (commande du joueur et réponse), sans sélection préalable.
- **Entrée** : envoyer la commande ; **Haut/Bas** : retrouver les dernières commandes.
- **Ctrl+S** : sauvegarder ; **Ctrl+Q** : sauvegarder et quitter.
- Une manœuvre à confirmer affiche les boutons **Tenter** et **Annuler**.

Le journal utilise du texte sélectionnable, avec un défilement qui ne saute pas en bas pendant
une sélection. La copie utilise le presse-papiers natif via Pyperclip, y compris sous Windows.
`Ctrl+C` ne ferme jamais le jeu, même sans sélection. Pour quitter, utiliser `Ctrl+Q`.

Le MJ travaille en arrière-plan. Pendant son appel, les panneaux restent consultables et
redimensionnables ; l’envoi d’une seconde action est désactivé pour éviter les doubles exécutions.
Quitter pendant un appel attend sa fin, puis sauvegarde. La fermeture brutale du terminal
ne peut pas assurer cette dernière sauvegarde.

Dans un terminal, la partie se joue par défaut dans le navigateur (`--web`, serveur local
127.0.0.1). Pour choisir explicitement l’affichage :

```powershell
python jeu.py --web
python jeu.py --tui
python jeu.py --console
```

Le mode console reste disponible sans Textual et est sélectionné automatiquement pour une
entrée ou une sortie redirigée. Sur une nouvelle installation :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-tui.txt
.\.venv\Scripts\python.exe jeu.py --tui
```
La partie reprend automatiquement depuis `sauvegardes/partie.json`.
`python jeu.py --new` démarre une nouvelle partie en conservant l'ancienne dans un fichier `.bak`.
`python jeu.py --offline` interdit les appels API et conserve les commandes locales.

Premiers essais, avec ou sans IA :

```text
examiner porte
examiner gravure
copier gravure avec cire
fiche
ouest
parler marchand
acheter pied-de-biche
est
retirer axe supérieur avec pied-de-biche
```

`aide` affiche les commandes. `carte`, `regarder`, `journal` et `inventaire` permettent de suivre l'état.

La carte utilise maintenant un plan métrique enregistré dans le monde : une case représente
1 m x 1 m, rendue sur deux colonnes et une ligne pour compenser approximativement les proportions
des caractères du terminal. L'antichambre mesure 6 x 4 m, l'échoppe 5 x 6 m ; la crypte possède
un renfoncement au nord. Les salles non visitées ne sont dessinées ni nommées : seuls le passage
et une flèche vers l'inexploré apparaissent. L'échoppe est déjà connue grâce au récit d'arrivée.

Les lettres A, E et C repèrent les salles dans la légende. `@` situe Corvus ; `k` désigne une clé,
`t` un luminaire éteint, `*` un luminaire allumé, `G` Gorm, `c` un coffre et `!` un outil.
Seuls les objets actuellement visibles dans la pièce sont dessinés. Les objets superposés portent
`&` ; ceux qui sont aux pieds du personnage sont précisés sous la carte. Prendre, poser et changer
de pièce mettent à jour les positions ; un contenu libéré reste à la position de son contenant.
Dans la TUI, la carte se rafraîchit après chaque commande. En console, elle est réaffichée à
l’arrivée et avec `regarder` ; `carte` affiche le plan seul.

La scène est décrite en un seul paragraphe, suivi des sorties. La fiche et la besace forment
un bloc distinct. Les compteurs de combustible sont réservés à la fiche et à l'examen des objets.
Les anciennes sauvegardes reçoivent le plan et des positions initiales à leur chargement,
sans remise à zéro de la progression.
Les axes doivent être retirés séparément. Une tentative peut échouer et fait passer du temps.
Le trésor peut être obtenu en dégondant, crochetant ou détruisant la porte, puis en ouvrant ou brisant le coffre.

Une démonstration reproductible va jusqu'au trésor sans utiliser l'API ni modifier la sauvegarde :

```powershell
python jeu.py --demo
```

### Questions et lumière

L'antichambre est sans fenêtre. Au départ, la lanterne que porte Corvus est allumée ; une torche
éteinte est au sol. La lueur du brasero de l'échoppe passe aussi par la sortie ouest.
Ces sources sont des objets du monde : on peut les examiner, les allumer ou les éteindre.
Le briquet de l'inventaire permet de rallumer une source encore utilisable.

```text
une sale sans fenetres, il fait tout noir ?
lumière
éteindre lanterne
examiner gravure
allumer lanterne
examiner gravure
```

La commande `lumière` explique la visibilité à partir de l'état réel, sans jet ni temps écoulé.
Un éclairage proche suffit à lire ; la lumière d'une pièce voisine perd un niveau en traversant une
ouverture. Une porte fermée ou un contenant opaque fermé arrête la lumière. Dans la pénombre,
on distingue les objets, mais on ne lit pas les inscriptions. Dans le noir, la liste visuelle des objets
est masquée. Les affaires de l'inventaire restent accessibles au toucher, ce qui permet le rallumage.
Palper un contenant ouvert et à portée révèle ce qu'il contient réellement, même dans la pénombre ;
un contenant vide est reconnu comme tel, sans inventer d'objets.
La lecture, la copie et l'extraction d'un axe exigent un éclairage suffisant. Une serrure
accessible peut être crochetée au toucher dans la pénombre, avec un jet plus difficile et plus long.

#### Lumière en cases

En mode cases (Relais, `--cases`), chaque source allumée éclaire directement les cases qu'elle
voit : pleine lumière jusqu'à 4 cases, pénombre jusqu'à 8 pour une lanterne, une torche ou un
brasero (`luminosite` 2 ; 2 et 4 cases pour 1, 6 et 12 pour 3), en distance réelle : les halos
sont ronds (pleine lumière à 4 cases droit devant, à 3 en diagonale). Murs, portes fermées et
obstacles opaques projettent une ombre. Une source éclaire aussi sa pièce, et la pièce voisine
par une ouverture, d'une lumière diffuse qui ne dépasse pas la pénombre. La lumière du jour
garde le modèle par pièce. Le niveau perçu, celui qu'exigent la lecture ou un geste précis, est
celui de la case du joueur : pour lire loin d'une source, il faut s'en approcher ou porter la
sienne. Une case recevant une lumière directe se voit jusqu'à 8 cases, une case dans la seule
pénombre diffuse jusqu'à 3. Depuis l'obscurité, une zone éclairée reste donc visible au loin
(`donjon/perception.py`, `CarteLumiere`). Sans cases, le modèle par pièce s'applique.

Pour obtenir le noir complet : aller à l'ouest, éteindre le brasero, revenir à l'est puis éteindre
la lanterne. La rallumer restaure la visibilité. Le combustible diminue avec le temps de jeu,
minute par minute avec la vie des PNJ : un feu qu'un PNJ recharge pendant une attente ne
s'éteint pas entre-temps. Les commandes d'observation ne le consomment pas. Un foyer
(`foyer: true`, le brasero) se recharge avec un combustible porté ou à portée de main
(`usages: ["combustible"]`, `charges`, `duree_combustion` en minutes par charge) : une
brassée se prend sur le tas sans emporter le stock. Pour allumer une source, il faut un outil
d'allumage ou une autre source allumée, portée ou à portée ; une source fixe ne vient pas à
soi : on lui apporte ce qu'on veut allumer. Le combustible d'autrui qu'on ne porte
pas doit d'abord être obtenu. Mettre un combustible dans un foyer (`deplacer` vers le foyer)
est le même geste ; un autre objet n'y entre pas, le feu ne brûle pas encore les objets
quelconques. Les autres sources ne se rechargent pas encore.

Avec le MJ, les phrases libres passent par `repondre_au_joueur` : soit une réponse narrative,
soit une proposition d’action. Le MJ rédige sa réponse à partir des faits publics, des événements
et des douze derniers échanges sauvegardés. Une question reçoit une réponse sans `tenter`, jet
ou temps écoulé. La conversation ne modifie ni les objets ni les caractéristiques.
Une proposition d'action physique faite en réponse à une question est refusée.
Hors ligne ou si l'authentification échoue, le jeu explique son indisponibilité : il ne fournit plus
automatiquement l'éclairage en réponse à toute question. Les commandes `lumière`, `regarder`,
`contexte` et `journal` restent disponibles. La détection locale des questions est seulement syntaxique.

Une prémisse est maintenant enregistrée dans le monde : Gorm a demandé à Corvus de retrouver
l’anneau, l’a conduit depuis son échoppe jusqu’à l’antichambre, puis est retourné à ses affaires.
L’échoppe est donc déjà connue sur la carte. Cette prémisse est écrite par l’auteur du scénario,
pas réinventée à chaque réponse. Les motivations personnelles de Corvus restent libres.
`contexte` rappelle ce départ et le dernier déplacement réel. La migration ajoute le récit et
la mémoire aux anciennes sauvegardes, en conservant les objets, les ressources et la progression.

Les anciennes sauvegardes sont enrichies à leur chargement, en conservant leur progression : ajout des
sources et du briquet, sans réinitialisation des objets existants. Si l'inventaire est plein, le nouvel
équipement est posé au sol. Une sauvegarde déjà enrichie conserve exactement l'état de ses lumières.

### Ce qui est réellement modélisé

| Fichier | Responsabilité |
|---|---|
| `donjon/monde.py` | Objets identifiés, composants, contenance, relations spatiales, perception, sauvegarde JSON |
| `donjon/moteur.py` | Préconditions, difficultés, jets, transitions atomiques, journal et mémoire des arbitrages |
| `donjon/enrichissement.py` | Compléments descriptifs des personnages, validation additive, détails examinables et persistance |
| `donjon/mj.py` | Conversation narrative ancrée dans les faits et propositions de manœuvres |
| `donjon/connexion.py` | Connexion OAuth, identité vérifiée, coffre protégé et renouvellement des jetons |
| `donjon/rendu.py` | Description de scène et fiche dérivées de l’état enregistré |
| `donjon/geometrie.py`, `donjon/carte.py` | Plans métriques, positions et carte ASCII limitée aux lieux explorés |
| `donjon/perception.py` | Sources lumineuses, transmission par les ouvertures, niveaux de visibilité et combustible |
| `donjon/commandes.py` | Petit analyseur local ; ce n'est pas un interprète général du français |
| `jeu.py` | Boucle commune à la console et à la TUI, sauvegarde et décision du joueur |
| `donjon/tui.py`, `donjon/tui.tcss` | Panneaux réactifs, saisie, journal et pont avec la boucle de jeu |

Une porte est un objet unique partagé entre deux pièces. Ses axes ne sont accessibles que du bon côté.
Les outils doivent être possédés et utilisables. L'examen est sans jet ; comprendre une inscription
demande un test d'INT. La cire est consommée, et chaque empreinte est un nouvel objet qui conserve son
motif si la source est détruite. Un outil servant de cale quitte l'inventaire et empêche la fermeture.

Un couteau peut tenter l'extraction d'un axe, mais le moteur impose une difficulté entre 17 et 22
et un risque d'endommagement sur un 1 naturel. Un levier adapté donne une difficulté entre 11 et 16
et un bonus d'outil. Le LLM choisit dans cette enveloppe : il ne peut pas accorder de réussite gratuite.
L'arbitrage est mémorisé par cible, outil, méthode et propriétés. Reformuler une tentative identique
ne change pas sa difficulté. Un changement réel de l'outil ou de la cible peut justifier un nouvel arbitrage.

Forcer (`frapper`, alias « forcer » et « défoncer ») suit une règle commune au joueur et aux PNJ
(`donjon/force.py`) : un outil qui fait choc (percussion, levier) ou qui coupe la cible ; d20 + FOR
modulée + 2 pour un outil de percussion contre 10, un 1 abîme l'outil ; un coup réussi ôte la
puissance de l'outil plus la FOR si elle aide. À zéro, une porte reste ouverte et déverrouillée, un
contenant s'ouvre et ce qu'il tenait tombe au sol. Chaque coup est bruyant. Un PNJ l'emploie comme
geste de son planificateur (`frapper`) : sur le bien d'autrui, c'est une faute au prix de son
honnêteté, et l'abîmer en est une autre au prix de sa douceur ; à 100, l'une ou l'autre l'exclut.

Les transitions sont préparées puis appliquées à une copie du monde, vérifiée avant validation.
L'IA ne peut ni injecter du Python ni transmettre une liste arbitraire de mutations. Elle peut composer
les opérations bornées décrites ci-dessous ; le moteur en déduit les effets autorisés. Les autres
actions restent des règles spécialisées. Les dés sont reproductibles à partir d'une graine et d'un
compteur sauvegardés. Les échecs consomment aussi le temps prévu et produisent le bruit prévu.

### Manœuvres composées

Le MJ peut proposer `action: composer` avec une à six étapes au lieu d'un verbe spécialisé.
Le langage comprend `patienter`, `deplacer`, `detacher`, `allumer`, `eteindre`, les gestes
d'appui et de son, ainsi que `ouvrir`, `fermer`, `deverrouiller`, `crocheter`, `couper`,
`frapper`, `bloquer` et `debloquer`, compilés avec les règles de l'action seule, et `alimenter`
(recharger un foyer avec un combustible porté ou à portée, une minute, sans jet ; `deplacer`
un combustible vers un foyer est ce geste ; une charge prolonge le
feu sans le rallumer ; commande locale `alimenter brasero avec fagots`) : « je crochète
la porte, je l'ouvre et je la cale avec le marteau » forme une seule séquence.
Les commandes locales `prendre`, `poser`, `voler`, `retirer`, `allumer` et `éteindre` sont traduites
vers ces mêmes opérations ; elles ne possèdent plus leur propre chemin de résolution.
Les effets (transfert, vol, détection, dommage à l'outil, réaction des témoins) sont calculés
par le moteur, jamais transmis librement par le modèle.

Exemples à essayer avec le MJ :

- « Je retire successivement les deux axes avec mon couteau et les laisse au sol. »
- « Je retire l'axe supérieur, le range dans ma besace, puis retire celui du bas. »
- « J'attends que Gorm soit distrait pour prendre discrètement les crochets. »
- « Je prends la torche et l'allume. » (briquet et combustible vérifiés, sans jet)
- Devant un contenant ouvert : « Je range mon couteau dans le coffre. »

Un déplacement vérifie la propriété, les attaches, l'accessibilité, la destination et
le poids, contenu compris. Une destination peut être la besace, le sol de la pièce ou
un contenant ouvert accessible. Le mode discret utilise la vigilance des témoins ;
déplacer ses propres affaires discrètement ne devient pas une accusation de vol.
Attendre deux minutes réduit de deux points la difficulté du déplacement discret suivant,
sans imposer l'inattention du PNJ et sans cumul du bonus. Extraire une fixation la dépose
au sol ; la ranger immédiatement ensuite ne consomme pas de minute supplémentaire.
Les objets créés par le MJ déclarent aussi leur relation au support : posés sur un support
qui peut porter, fixés à un élément immobile, ou placés dans un contenant ouvert. Une prise
d'objet fixé exige d'abord son détachement ; une attache simple se libère sans outil ni jet.
La relation est enregistrée avec l'objet et reste visible après rechargement.

Le moteur vérifie toute la séquence sur une projection avant de lancer les dés, y compris
la lumière qui peut s'éteindre entre deux étapes. Une séquence impossible est refusée sans
effet. À l'exécution, chaque étape est revalidée ; le premier échec arrête la suite et conserve
les étapes déjà réussies ainsi que leurs coûts. Les traces du journal détaillent les jets,
les effets appliqués et les étapes exécutées. Les arbitrages d'extraction restent mémorisés
selon les propriétés physiques pertinentes ; une reformulation ne change pas la difficulté.

Les plans du MJ sans jet s'exécutent directement ; les plans risqués attendent `tenter`.
Après une manœuvre composée, le résultat est sauvegardé puis envoyé au LLM pour un récit
sans pouvoir de modification. Une panne de narration affiche le résultat local et ne
rejoue jamais la manœuvre. Cela ajoute un appel de narration. En mode comparaison, les
deux modèles proposent leurs opérations sur des copies ; leurs narrations comparent ensuite
le même résultat réellement obtenu dans la partie, dans une nouvelle entrée de debug.

Ce langage est une première extension, pas une physique générale : les extractions portent
encore sur les fixations amovibles modélisées, le portage limite aussi les déplacements,
et les routines de PNJ, distractions élaborées, combat ou nouvelles familles d'effets
nécessitent encore des règles. Les contenants n'ont pas encore de limite de volume.

### Dialogues et récompenses

Adresse une question à un personnage présent, par exemple : « Gorm, qu'est-ce que
je gagne à retrouver cet anneau ? ». Le MJ conserve le sujet, propose une opération
au moteur, puis formule la réponse du personnage à partir du résultat validé.
Ces conversations utilisent deux appels au modèle ; les commandes locales n'en utilisent aucun.
Le second appel reçoit des consignes de rédaction séparées, sans les consignes de
proposition du premier appel. Il ne peut produire qu'un dialogue non vide. Une discussion
sans changement d'accord utilise quand même les faits disponibles pour répondre.
Une réponse vide est signalée comme telle ; aucun changement n'est enregistré et la
réponse brute reste visible dans les traces du comparateur.

Gorm propose 20 pièces pour l'anneau du veilleur. Tu peux négocier, accepter ou
refuser. La négociation dépend du Charisme et des fonds disponibles : avec le
Corvus initial, Gorm peut monter à 22 pièces. Une question sur la récompense
n'accepte pas l'offre à ta place. L'accord accepté reste fixe dans ce prototype.

L'offre, l'accord et le paiement sont des états distincts conservés dans la sauvegarde
et affichés sur la fiche, ainsi que par `accords`. Pour être payé, il faut porter
l'anneau et le remettre à Gorm en sa présence. Le moteur transfère l'objet et
l'argent une seule fois. Gorm possède une bourse finie ; les offres en cours réservent
les montants promis. Le MJ ne peut pas créer de récompense hors des missions configurées.

Commandes disponibles aussi hors ligne : `offre marchand`, `negocier marchand 25`,
`accepter offre`, `refuser offre`, `remettre anneau` (ou `remettre anneau à Gorm`).
Les profils, missions et finances sont configurés dans `donjon/dialogues.py` ; le
mécanisme fonctionne avec d'autres personnages configurés. Les anciennes sauvegardes
reçoivent ces données sans réinitialiser la progression ni accepter d'offre automatiquement.
Le comparateur montre également le résultat appliqué et l'engagement enregistré côté principal.

### Vol et vigilance

« J'attends que Gorm ait le dos tourné pour prendre discrètement les crochets » est
une tentative de vol : le MJ propose `voler`, méthode `finesse`. Le moteur fixe le jet
de DEX contre la vigilance des PNJ présents. Attendre une occasion prend trois minutes
et réduit la difficulté de deux points ; un vol direct prend une minute. Le bruit, un
objet encombrant et les soupçons augmentent la difficulté. L'attente ne garantit pas
que le personnage se détournera. Comme les autres actions risquées proposées par le
MJ, la tentative est annoncée puis exécutée avec `tenter`.

En cas de réussite, l'objet rejoint la besace sans paiement, disparaît de la carte et
n'est plus en vente. Il garde la trace de son propriétaire ; les PNJ ne sont pas informés
d'un vol passé inaperçu. En cas d'échec, les témoins présents surprennent le geste,
l'objet reste en place et leur méfiance augmente. Gorm refuse alors de vendre, mais les
récompenses déjà convenues restent dues. Ces incidents persistent après rechargement ;
attendre ne les efface pas. Les dialogues reçoivent cette relation avec le joueur.

Hors ligne, `voler crochets` ou `dérober crochets` exécute directement une tentative.
`prendre crochets` reste refusé pour éviter d'interpréter une simple commande comme un
vol. Seuls les objets accessibles, transportables et appartenant à autrui sont concernés.
Sans témoin, c'est-à-dire sans personnage qui perçoit le joueur, il n'y a pas de jet de
discrétion. Un PNJ qui revoit vide la place d'un objet qui lui appartient le note dans sa
mémoire et ses biens sont relancés ; il ne sait pas qui l'a pris. Un vol surpris lui fait
cesser de croire le joueur fiable.

### Connaissances des personnages

Chaque PNJ dispose de `savoirs_pnj` dans la sauvegarde. Les savoirs d'auteur ont l'origine
`jeu` ; les compléments du modèle ont l'origine `MJ`, avec leur révision de création.
Gorm connaît notamment le crochetage et les axes amovibles de la porte de la crypte.
Ces connaissances décrivent sa construction, sans lui donner la vision de son état à distance.
Le contexte du modèle ne contient que les connaissances des personnages présents.

Lorsqu'un sujet narratif manque, le MJ peut proposer `enrichir_savoirs`. Une contre-revue
classe la portée de chaque phrase : le souvenir ou la croyance du PNJ peut être enregistré,
mais une affirmation autonome sur le monde ou la quête exige un autre fait validé.
L'ajout est sauvegardé avant affichage.
Il reste disponible après un redémarrage et indépendamment des douze échanges récents.
Une connaissance existante ne peut pas être remplacée par un autre récit.
Exemples : « Gorm, pourquoi tiens-tu à cet anneau ? », puis plus tard « Rappelle-moi pourquoi ».

Les sujets ouverts à l'invention sont configurés par personnage dans `sujets_savoirs_pnj` :
apprentissage, souvenir personnel, tradition locale, motivation, et lien à l'anneau pour Gorm.
Un dictionnaire vide désactive l'invention pour un personnage. Les autres PNJ bénéficient
du même mécanisme sans recevoir les connaissances de Gorm. Configuration initiale :
`donjon/connaissances.py`. Le debug montre les connaissances proposées par les deux modèles
et celles effectivement enregistrées par le principal ; le secondaire reste isolé.

Les connaissances inventées sont narratives : elles ne créent ni objet, ni passage,
ni pouvoir, ni récompense dans le moteur. La validation contrôle le personnage, les sujets
autorisés, les doublons et la transaction. La compatibilité sémantique du texte libre avec
les autres récits dépend encore du modèle ; ce n'est pas un système de preuve automatique.
Les secrets et les mécanismes de quête restent définis par le jeu. L'apprentissage par
observation autonome, les mensonges et la propagation de rumeurs ne sont pas simulés.

### Ambiance et budget d'invention

Luna décrit librement l'ambiance (aspect, odeur, son de fond, impression) ; elle est
enregistrée par lieu et revient dans son contexte pour rester cohérente. Un élément
d'ambiance que le joueur veut manipuler est établi comme objet ou détail par le moteur,
puis l'intention est réexaminée sans que le joueur la répète ; sinon Luna explique qu'il
ne se manipule pas.

Chaque lieu peut déclarer `potentiel_invention` : nombre d'objets que le MJ peut y faire
apparaître, masse maximale et capacités permises (`son`, `lumiere`, `tranchable`, `couper`,
`levier`, `allumage`). Une place consommée le reste, même si l'objet est emporté. Les trois
scénarios déclarent 2 objets, 3 kg, `son` et `tranchable` : Luna peut enrichir un lieu sans
fournir une source de lumière ou un outil qui contournerait une énigme.

Les résultats d'action sont racontés par Luna après application et sauvegarde ; le texte du
moteur reste dans le journal et sert de repli. `--recit-moteur` garde le rendu du moteur.

### Limites de cette première version

- C'est une expérience d'interactions avec des objets, pas une simulation mécanique générale.
  Le battant devient un passage libre une fois les deux axes retirés : sa chute, son équilibre
  et l'arrachement de la serrure sont simplifiés. Les dégâts aux murs ne créent pas de nouvelles pièces.
- Le MJ interprète les intentions, compose les opérations disponibles et arbitre les extractions ;
  les autres difficultés suivent les règles du moteur, notamment vigilance et soupçons.
  Il ne crée pas de règles nouvelles, de propriétés mécaniques manquantes ou de nouvelles familles d'effets.
  Une action hors de ce vocabulaire doit être annoncée comme non prise en charge.
- La faisabilité sémantique du choix du modèle n'est pas prouvée par la validation du JSON.
  Le moteur bloque certaines incohérences concrètes ; il ne peut pas vérifier tout le raisonnement du LLM.
- Les dialogues des personnages présents tiennent compte du sujet et des faits connus.
  Les engagements économiques sont limités aux récompenses des missions configurées ;
  pas encore de promesses libres, de réputation ou de négociation des prix de boutique.
  Le bruit modifie l'humeur du marchand ; il n'y a ni combat ni IA tactique.
  Les PV et PER sont présents sur la fiche mais sans mécanique dédiée pour l'instant.
- Le MJ peut compléter à la demande la description de **tout personnage connu ou visible en pleine lumière** :
  âge apparent, silhouette, visage, cheveux, yeux, barbe, mains, voix et tempérament apparent.
  Par exemple : « De quelle couleur sont les yeux de Gorm ? ». Il propose les ajouts au moteur,
  puis reçoit les faits validés pour répondre. Les contrôles de narration et de portée ajoutent
  des appels au modèle. Aucun supplément d'action, de temps ou de jet.
  Les détails corporels deviennent des cibles pour `examiner` et `toucher`, puis sont conservés dans
  la sauvegarde et la mémoire des rencontres. Le combat et les transformations corporelles restent hors modèle.
  `examiner <personnage>` utilise aussi le MJ si le personnage n'a encore aucun portrait ; hors ligne,
  seuls les faits déjà enregistrés sont affichés. Les détails sont enregistrés avant d'afficher la réponse.
  La TUI actualise la scène après leur enregistrement.
- Un complément ne remplace aucune facette existante. Il ne crée ni équipement, ni PNJ,
  ni caractéristique, ni récompense, ni secret de quête. Le moteur vérifie les cibles, les champs
  autorisés, les doublons et la transaction ; un contrôle de portée fait corriger les descriptions
  qui impliquent un fait autonome, mais sa classification sémantique n'est pas une preuve formelle.
  Les portraits d'auteur
  restent prioritaires. Les ajouts du MJ sont traçables dans `enrichissements` dans la sauvegarde.
- Le MJ peut proposer dans une même transaction des faits typés : détail visible sur un support,
  inscription et parole d'un PNJ présent. Le moteur vérifie les ancrages et la perception, crée
  les cibles ou enregistre le locuteur et les auditeurs, puis compose le texte affiché. Les ajouts
  sont sauvegardés avant affichage ; une inscription reste examinable et lisible. Les dialogues
  libres sont contrôlés séparément (voir contrat-mj.md).
- La mémoire permet de décrire un personnage rencontré même hors de sa pièce, sans révéler son humeur
  actuelle. Les souvenirs visuels sont actualisés lors des actions en présence du personnage et en pleine
  lumière. La rencontre initiale et le premier portrait de Gorm sont établis par la prémisse.
  Le prototype ne garantit pas la compatibilité des anciennes sauvegardes entre versions.
- La carte respecte les dimensions et les positions enregistrées ; la forme des salles non visitées reste cachée.
  Sans `--cases`, les déplacements se font de pièce en pièce ; le mode cases (lanceurs par défaut)
  ajoute la navigation case par case, la portée de manipulation et la ligne de vue.
- L'éclairage utilise trois niveaux discrets calculés par pièce, sans portée métrique en cases,
  ombres ou calcul physique des flammes.
  Pas de calcul mécanique des leviers. L'enrichissement du décor exige encore un support existant.
- Dans le noir, la navigation par les directions du plan reste simplifiée ; les surfaces doivent être
  connues pour être ciblées au toucher. Les descriptions tactiles ne reproduisent pas les détails visuels.
- Sauvegarde destinée à une seule instance du jeu à la fois. `--debug` autorise `etat <objet>` et
  expose volontairement les données internes de la cible visible pour mettre au point le prototype.
