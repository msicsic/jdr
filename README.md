# Le Seuil

Prototype de JDR ASCII en français, Python 3.11 ou supérieur. L’interface plein écran utilise Textual. Le moteur et le mode console hors ligne
utilisent la bibliothèque standard ; la connexion au forfait ChatGPT utilise PyJWT[crypto].
Le joueur explore trois pièces, s'équipe chez Gorm et cherche l'anneau du veilleur.
Le mode console affiche `prototype testvrac` et le chemin du projet pour identifier cette version.
La porte de la crypte sert de terrain d'essai : gravure, serrure, deux axes amovibles,
outils fragiles ou robustes, empreinte en cire et cale récupérable.

## Défi du Relais des crues et déplacement en cases

Double-cliquer sur **`lancer-defi.cmd`** pour une nouvelle scène avec **Luna seul**.
**`lancer-defi-hors-ligne.cmd`** lance exactement le même défi sans aucun appel au LLM.
Retrouver la cloche d'alarme du relais et la rapporter au refuge : un indice, des recoins
à explorer et plusieurs accès permettent de choisir son itinéraire. Aucun chronomètre
de défaite : on peut prendre le temps de réfléchir.

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
- Les objets doivent être sur la même case ou une case voisine pour être manipulés.
  Il faut s'approcher pour lire les petits détails ; les murs, les portes et les obstacles
  opaques bloquent la vue. Les objets pris quittent immédiatement la carte.

La carte garde le terrain exploré et distingue ce qui est visible maintenant. Dans la TUI,
les cases visibles sont vert sombre et les cases explorées hors de vue bleu ardoise ; une
légère alternance de teinte laisse compter les pas. La console conserve `.` pour le terrain
visible et `:` pour le terrain mémorisé.
Les murs sont des blocs `##`, y compris dans les angles. `+` désigne uniquement une porte
fermée, `X` une porte verrouillée et `/` une porte ouverte dans ce mode.
Les lieux encore inconnus restent blancs. Les niveaux explorés restent affichés ensemble ;
une échelle installée porte le même repère `H1` à ses deux extrémités. Un objet déjà vu
hors du champ de vision garde son symbole à sa dernière position observée, en gris bleuté
dans la TUI. Ce souvenir peut être périmé : il s'efface si la case est revue vide ou si le
joueur prend l'objet. La console sans couleur préfixe ce symbole par `~`. Une case représente un mètre,
affiché sur deux colonnes pour conserver des proportions lisibles dans le terminal.
Le dernier état vu d'une porte reste également indiqué hors de vue, avec la même couleur
de souvenir. Il peut avoir changé depuis ; la carte l'actualise quand le seuil est revu.

Dix pas dépensent une minute et consomment le combustible correspondant. Franchir un seuil
ou un escalier est une transition vers la première case de l'autre côté. La lumière utilise
encore des niveaux par pièce ; la ligne de vue et les obstacles sont calculés case par case.
Les touches de déplacement, les collisions, la visibilité et les commandes locales sont
entièrement déterministes et ne consomment aucun appel au LLM. Le MJ reçoit les objets
perceptibles et leur portée, puis le moteur vérifie aussi ses propositions d'action.

Les lanceurs du donjon et de l'atelier activent également ce mode. En ligne de commande :

```powershell
.\.venv\Scripts\python.exe jeu.py --defi --tui --offline
.\.venv\Scripts\python.exe jeu.py --atelier --cases --tui --model gpt-6-luna
```

## Atelier : premier harnais de fabrication

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

### Franchissement improvisé avec un appui mobile

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
Un refus initial du MJ est réexaminé une fois si ce dossier comporte une méthode admissible,
sans forcer une réussite ni contourner un obstacle réel. `tools/test_saut_reel.py` vérifie la
phrase avec Luna seul, puis résout réussite et échec sur des copies en mémoire.

Le harnais fournit à Luna un dossier calculé localement : ressources, mesures manquantes,
proposition réalisable si disponible, consommation et durée. Les intentions de fabrication
utilisent des instructions ciblées. Une proposition d'action invalide reçoit l'obstacle exact
et **un seul essai de correction**, sans effet sur le monde avant résolution. Une question
ne déclenche pas de fabrication. La narration du résultat reçoit un contexte réduit.
Les commandes connues restent locales ; aucun second modèle ni modèle de secours n'est lancé.

« Je retente » ou « je réessaie » reprend la dernière tentative échouée sans appel
d'interprétation au LLM : même méthode, ressources revalidées, étapes déjà réussies exclues.
Une tentative risquée attend toujours **tenter**. Pour changer de méthode après un échec,
préciser par exemple « Cette fois je prends mon temps pour fabriquer soigneusement l'échelle ».
Une narration peut ensuite utiliser le modèle, comme pour les autres actions.
Le contexte du MJ contient aussi la dernière tentative résolue et les quantités exactes de lien
disponibles/requises, pour éviter les clarifications inutiles et les fausses annonces de pénurie.

`F5` en mode debug montre les réponses, propositions, usages et refus de validation de Luna.
Les traces sont aussi enregistrées dans `artifacts/mj/`, sans clés ni jetons. Les informations
techniques restent hors de la chronique. Pour une action valide : un appel d'interprétation,
puis un appel de narration après exécution ; une correction peut ajouter un appel.

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

## Jouer

### Détails du personnage joueur

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

### Improviser une action hors du catalogue

Le MJ dispose d'un arbitrage sommaire `improviser` : intention, cibles, outil, durée,
bruit, éventuel jet et deux issues conditionnelles. S'étirer ou fredonner ne demandent
pas de règle dédiée ni de jet. Un refus fondé sur une limite technique est réexaminé
une seule fois, avec le même modèle. Le schéma est disponible dès le premier appel :
aucun appel supplémentaire systématique et aucun second modèle.
Le récit des deux issues est fourni dans cet appel ; seule l'issue effectivement résolue
est affichée. Ces arbitrages n'utilisent donc pas un second appel de narration.

La résolution est validée sur une copie puis appliquée et journalisée par le moteur.
Les gestes passés reviennent dans le contexte ; une marque devient un détail réel,
examinable sur son support et conservé dans la sauvegarde. Les sons laissent un souvenir
aux PNJ à portée. Les mouvements d'objets réutilisent les contrôles de propriété,
d'accessibilité, de poids et d'attaches. Les blessures de cet arbitrage sont limitées
à 3 PV au total et ne peuvent tuer ; blessures et usure exigent une tentative confirmée.
Une difficulté est mémorisée pour la même intention et les mêmes conditions pertinentes.

Exemples : « je m'étire », « je fredonne une chanson », « je grave une flèche sur la perche
avec mon couteau », « je jongle avec la clé ». Une chute d'objet racontée doit correspondre
à un déplacement effectif dans la branche concernée. Les tests réels sont dans
`tools/test_improvisation_reel.py` et n'utilisent aucune sauvegarde du joueur.

La prose reste proposée par le LLM : le moteur vérifie les effets structurés, pas la vérité
de chaque phrase libre. Elle ne doit pas établir de propriétés mécaniques supplémentaires.
L'improvisation ne remplace pas la géométrie pour un franchissement, les règles de fabrication
pour un nouvel objet fonctionnel, ni les mécanismes de dialogue pour un engagement de PNJ.

### Abords, déplacements d'échelle et sauts

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

### Appeler, crier et siffler

`je crie à l'aide`, `crier au secours`, `crier` et `siffler` fonctionnent aussi hors ligne,
sans appel au modèle ni jet de dés. Les formulations libres passent par Luna avec l'opération
composable `emettre_son`. Un son coûte une minute et augmente le bruit.

L'audition suit les connexions établies : perte d'un niveau par ouverture, de deux derrière
une porte fermée. Les paliers reliés par un appui vertical transmettent aussi le son. Les
lieux non reliés restent hors de portée ; il ne s'agit pas d'un calcul acoustique métrique.
Les PNJ à portée conservent leur dernier son entendu, sans révéler leur identité au joueur
s'ils sont hors de sa perception. Ce souvenir est fourni au dialogue lorsqu'on les rencontre.
Le cri ne décide ni de leur réponse ni de leur déplacement, et ne crée pas de sauveteur.
La restitution peut donc être : « Tu cries à l'aide. Pour l'instant, aucune réponse ne te parvient. »

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

Pour choisir explicitement l’affichage :

```powershell
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

## Questions et lumière

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
La lecture, la copie et l'extraction d'un axe exigent un éclairage suffisant. Une serrure
accessible peut être crochetée au toucher dans la pénombre, avec un jet plus difficile et plus long.

Pour obtenir le noir complet : aller à l'ouest, éteindre le brasero, revenir à l'est puis éteindre
la lanterne. La rallumer restaure la visibilité. Le combustible diminue avec le temps de jeu ;
les commandes d'observation ne le consomment pas. Le ravitaillement n'est pas encore simulé.

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

## Activer le MJ IA

### Avec le forfait ChatGPT

Le jeu propose le flux officiel « Sign in with ChatGPT » pour les comptes et forfaits éligibles.
Il ne récupère pas les identifiants de Codex ou d'autres applications. L'autorisation se fait dans
le navigateur avec votre compte ChatGPT ; cela n'achète ni abonnement ni crédits.

Depuis le terminal, si la dépendance n'est pas déjà installée :

```powershell
python -m pip install -r requirements-chatgpt.txt
python connexion.py connecter
python jeu.py --connexion chatgpt
```

On peut aussi lancer le jeu sans `--offline`, puis saisir `connecter` dans le jeu. La commande
`connexion` affiche le mode en cours. Après une connexion réussie dans le navigateur, le jeu utilise
directement le forfait. Son utilisation reste soumise aux limites du compte.

Les modèles accessibles au compte se consultent ainsi :

```powershell
python connexion.py modeles
python jeu.py --connexion chatgpt --model gpt-6-luna
```

Le modèle demandé est vérifié dans le catalogue du compte avant le premier appel. Aucun modèle
de substitution n'est choisi silencieusement. `python connexion.py statut` liste les inscriptions
sans afficher les jetons ; `connecter --nouveau` ajoute un autre compte et `connecter --compte <id>`
réutilise une inscription. `python connexion.py deconnecter` révoque la session si possible,
efface les jetons locaux et conserve l'identifiant d'inscription pour une connexion ultérieure.

Les identifiants du jeu sont isolés dans `.seuil-auth/`, exclu de Git. Les jetons sont chiffrés avec
DPAPI sous Windows (liés au compte Windows) ; sur Unix, le répertoire et les fichiers sont privés.
Les retours OAuth vérifient `state`, PKCE, la signature du jeton d'identité, son émetteur,
son audience, sa durée de validité et son nonce. L'autorisation d'utiliser le forfait est vérifiée
séparément. Un verrou évite les rafraîchissements concurrents du même coffre.

Le transport forfait impose `store: false`, `stream: true` et des outils placés dans un namespace.
Un fragment de réponse n'est jamais exécuté : seul `response.completed` valide la proposition.
Les erreurs de forfait ne déclenchent aucun basculement vers une clé API facturée séparément.

Par défaut, le jeu privilégie une inscription ChatGPT enregistrée. `--connexion api` choisit
explicitement la clé API ; `--offline` interdit toute connexion, y compris la commande `connecter`.

### Avec une clé API

Le connecteur utilise l'API OpenAI Responses et un appel de fonction strict `repondre_au_joueur`.
`proposer_action` reste disponible pour les tests d’arbitrage seuls.
La clé vient de `OPENAI_API_KEY`. On peut également copier `.env.example` vers `.env` et
y renseigner la clé localement. Les valeurs non vides du `.env` priment sur celles du terminal.
Ni la clé ni les en-têtes d'authentification ne sont enregistrés dans la sauvegarde.

Le modèle par défaut est `gpt-6-luna`, avec un effort de raisonnement `medium`.
Il est configurable via `OPENAI_MODEL`, le `.env` ou `--model` :

```powershell
python jeu.py --model gpt-6-luna --effort medium
```

Le modèle choisi doit être accessible avec votre compte et prendre en charge Responses,
les appels de fonction stricts et `reasoning.effort`. Aucun changement de modèle automatique n'est effectué.

Une phrase libre appelle le MJ. Le préfixe `mj` force ce chemin :

```text
mj Je glisse mon couteau sous la tête de l'axe supérieur et fais doucement levier.
tenter
```

Le MJ propose une seule manœuvre, son outil et, pour l'extraction d'une fixation, sa difficulté.
Une action simple et explicite (« je prend la clé ») est validée puis exécutée directement.
Si une manœuvre interprétée par le MJ exige un jet ou comporte un risque, le jeu affiche le test,
la durée et le risque : `tenter` applique alors la proposition ; `annuler` l'abandonne.
Les commandes locales explicites gardent leur exécution directe.
Les observations et examens sont affichés immédiatement.
Discuter avec le MJ conserve la proposition en attente ; une autre action la remplace.
Le MJ reçoit explicitement cette proposition afin de distinguer ce qui reste à tenter d’un résultat acquis.
Le moteur recompilé au moment d'agir vérifie que l'état n'a pas changé.

Les commandes locales n'appellent pas l'API. Chaque phrase transmise au MJ déclenche au maximum
un appel, décompté du forfait ou facturé sur le compte API, sans relance automatique. L’appel contient
l’intention, la scène perceptible, la fiche, la prémisse, les six derniers événements et les douze
derniers échanges. Les paroles du joueur et du MJ sont séparées des faits du moteur. Le trésor encore caché et le sens
non déchiffré de la gravure sont exclus de cette vue. `store` vaut `false`.
La réponse de conversation vient du LLM ; les résultats d’actions restent décrits par le moteur,
sans second appel au modèle. Les références de faits du dialogue sont contrôlées, mais ce contrôle
ne prouve pas que chaque phrase les reformule fidèlement. Une hallucination narrative reste possible ;
elle n’est jamais ajoutée automatiquement à l’état physique ou au scénario.

En cas de clé invalide, délai réseau ou réponse incorrecte, l'action n'est pas appliquée.
Une erreur 401 coupe les appels répétés pour cette session ; connecter le forfait recrée un client.
Les commandes locales restent utilisables. La présence d'une clé ne signifie pas qu'elle est valide :
la bannière indique que la connexion sera vérifiée au premier échange.

## Ce qui est réellement modélisé

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

Les transitions sont préparées puis appliquées à une copie du monde, vérifiée avant validation.
L'IA ne peut ni injecter du Python ni transmettre une liste arbitraire de mutations. Elle peut composer
les opérations bornées décrites ci-dessous ; le moteur en déduit les effets autorisés. Les autres
actions restent des règles spécialisées. Les dés sont reproductibles à partir d'une graine et d'un
compteur sauvegardés. Les échecs consomment aussi le temps prévu et produisent le bruit prévu.

## Manœuvres composées

Le MJ peut proposer `action: composer` avec une à six étapes au lieu d'un verbe spécialisé.
Le langage comprend `patienter`, `deplacer`, `detacher`, `allumer` et `eteindre`.
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

## Dialogues et récompenses

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

## Vol et vigilance

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
Sans témoin présent, il n'y a pas de jet de discrétion. La surveillance reste simplifiée
à la pièce entière : pas encore de champ de vision, routine de déplacement, découverte
ultérieure d'un objet manquant ou mécanisme de réconciliation.

## Connaissances des personnages

Chaque PNJ dispose de `savoirs_pnj` dans la sauvegarde. Les savoirs d'auteur ont l'origine
`jeu` ; les compléments du modèle ont l'origine `MJ`, avec leur révision de création.
Gorm connaît notamment le crochetage et les axes amovibles de la porte de la crypte.
Ces connaissances décrivent sa construction, sans lui donner la vision de son état à distance.
Le contexte du modèle ne contient que les connaissances des personnages présents.

Lorsqu'un sujet narratif manque, le MJ peut proposer `enrichir_savoirs`, puis reçoit les
connaissances validées pour rédiger sa réponse. L'ajout est sauvegardé avant affichage.
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

## Limites de cette première version

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
  puis reçoit les faits validés pour répondre. Deux appels au maximum sont nécessaires lors d'un
  enrichissement ; une réponse ordinaire reste à un appel. Aucun supplément d'action, de temps ou de jet.
  Les détails corporels deviennent des cibles pour `examiner` et `toucher`, puis sont conservés dans
  la sauvegarde et la mémoire des rencontres. Le combat et les transformations corporelles restent hors modèle.
  `examiner <personnage>` utilise aussi le MJ si le personnage n'a encore aucun portrait ; hors ligne,
  seuls les faits déjà enregistrés sont affichés. Les détails sont enregistrés avant d'afficher la réponse.
  La TUI actualise la scène après leur enregistrement.
- Un complément ne remplace aucune facette existante. Il ne crée ni équipement, ni PNJ,
  ni caractéristique, ni récompense, ni secret de quête. Le moteur vérifie les cibles, les champs
  autorisés, les doublons et la transaction ; la cohérence **sémantique du texte libre** repose encore
  sur le respect des consignes par le modèle, pas sur une preuve automatique. Les portraits d'auteur
  restent prioritaires. Les ajouts du MJ sont traçables dans `enrichissements` dans la sauvegarde.
- La mémoire permet de décrire un personnage rencontré même hors de sa pièce, sans révéler son humeur
  actuelle. Les souvenirs visuels sont actualisés lors des actions en présence du personnage et en pleine
  lumière. La rencontre initiale et le premier portrait de Gorm sont établis par la prémisse. Les anciennes
  sauvegardes restent compatibles et leur progression est conservée.
- La carte respecte les dimensions et les positions enregistrées ; la forme des salles non visitées reste cachée.
  Les déplacements restent de pièce en pièce : pas encore de navigation case par case ni de calcul de portée
  pour les interactions. Le plan des salles déjà visitées reste consultable dans le noir ; leurs objets ne sont
  affichés que lorsqu’ils sont visibles dans la pièce actuelle. La taille des salles est révélée à leur entrée.
- L'éclairage utilise trois niveaux discrets, sans portée métrique, ombres ou calcul physique des flammes.
  Pas de calcul mécanique des leviers. L'enrichissement ne couvre pas encore les décors et les objets ordinaires.
- Dans le noir, la navigation par les directions du plan reste simplifiée ; les surfaces doivent être
  connues pour être ciblées au toucher. Les descriptions tactiles ne reproduisent pas les détails visuels.
- Sauvegarde destinée à une seule instance du jeu à la fois. `--debug` autorise `etat <objet>` et
  expose volontairement les données internes de la cible visible pour mettre au point le prototype.

## Comparer deux modèles pendant une partie

**`lancer.cmd` et `lancer-debug.cmd` utilisent Luna seul.** Le second lanceur ajoute les traces
locales dans `artifacts/mj/` et les commandes d'inspection, sans appel à un autre modèle.
La comparaison reste disponible uniquement sur demande explicite avec `--compare-model`.
Elle utilise la même connexion (forfait ChatGPT ou clé API) ; les appels supplémentaires
consomment donc cette connexion.

Pour choisir les modèles et l'effort de raisonnement :

```powershell
.\.venv\Scripts\python.exe jeu.py --tui --debug --model gpt-6.1-sol --compare-model gpt-6-luna
```

`--compare-effort low` change seulement l'effort du secondaire ; par défaut il est identique au principal.
`--debug` seul autorise l'inspection des objets et ne lance aucun second modèle.
Les données d'usage ne sont pas imprimées dans la Chronique ; les compteurs de tokens
restent dans le panneau de comparaison et les données détaillées dans ses journaux.

- **F5** ouvre ou ferme la console de comparaison. Les colonnes montrent les textes, les faits
  proposés, les actions, la validation du moteur, la durée et les tokens additionnés sur tous les appels
  de l'échange. Les faits refusés sont également visibles. Sur un terminal étroit, les colonnes s'empilent.
- La souris permet de sélectionner et faire défiler le texte ; **Ctrl+C** copie la sélection.
  **F4** copie toute la comparaison affichée. Les boutons permettent de parcourir les 100 dernières
  comparaisons de ce lancement. F2/F3 reviennent au jeu.
- Chaque demande au MJ part de **deux copies identiques** du monde, de l'historique et de la proposition
  en attente. Les premières requêtes ont la même empreinte, hors modèle et effort. Si un modèle propose
  un enrichissement, son appel de narration reçoit ses propres ajouts validés sur sa copie : ces seconds
  appels peuvent donc différer. Au tour suivant, tous deux repartent de la partie réelle du principal.
- **Seul le principal pilote la partie.** Le secondaire ne lance jamais de jet et n'enregistre aucun fait
  dans la sauvegarde. Il reste en arrière-plan ; son erreur ou sa lenteur n'empêchent pas de jouer.
  Si les demandes se succèdent trop vite, le secondaire les traite dans l'ordre sur leurs instantanés
  respectifs (huit en attente maximum, tout dépassement est signalé). À la fermeture, les demandes en
  attente sont abandonnées ; un appel déjà envoyé peut tout de même être consommé côté fournisseur.
- Les commandes purement locales ne déclenchent aucune comparaison. `--offline` interdit les deux modèles.
  En mode `--console`, saisir `comparaison` affiche le dernier état des résultats sans entremêler les
  sorties du secondaire avec la saisie du joueur.

Les traces sont enregistrées dans `artifacts/comparaisons/comparaison-*.jsonl` (un fichier par lancement,
plusieurs versions d'une même comparaison, repérées par `numero` et `version`). Elles contiennent les
questions, réponses, propositions, erreurs et usages, sans clés ni jetons d'authentification.
Une panne d'écriture du journal est signalée dans la console debug et ne bloque pas le jeu.

`tools/test_comparaison_reel.py` teste une question sur les yeux de Gorm avec les deux modèles : deux
à quatre appels réels, aucun changement de la sauvegarde utilisateur. `tools/apercu_comparaison.py`
produit des captures de l'interface avec des réponses simulées, hors ligne.

## Vérification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
python jeu.py --demo
```

Les tests couvrent notamment l'accès depuis le bon côté, la non-divulgation des secrets,
les objets et outils absents, les achats, les risques, l'empreinte persistante, les portes calées,
la destruction de contenants, l'atomicité, la sauvegarde et le contrat API avec réponses simulées.
Ils couvrent aussi la question exacte ci-dessus, les réponses sans action, le noir complet, le rallumage,
la lumière bloquée par les portes ou contenants, la consommation du combustible et la migration des sauvegardes.

Un test distinct effectue **quatre véritables appels**, décomptés du forfait ou facturés à la clé API :
question sur l'arrivée, question sur la lumière, extraction plausible d'un petit axe au couteau,
puis tentative impossible de soulever tout le battant avec la lame. Il ne modifie aucune partie :

```powershell
python tools/test_mj_reel.py
```

Le test narratif utilise **six appels réels** dans une conversation suivie, sans toucher à la
sauvegarde utilisateur :

```powershell
python tools/test_recit_reel.py --connexion chatgpt
```

`python tools/test_personnages_reel.py` effectue deux appels réels supplémentaires pour vérifier
le portrait de Gorm malgré une ancienne réponse erronée, puis la distinction entre souvenir
et humeur actuelle à distance. Il ne modifie aucune sauvegarde.

`python tools/test_enrichissement_reel.py` teste trois questions (au plus six appels réels) :
création d'un détail de Gorm, rappel identique après sauvegarde/rechargement et portrait d'un autre
personnage sans description initiale. Le test emploie une partie temporaire et vérifie aussi l'examen
local des détails créés. Les tests automatiques couvrent les refus de modification, les échecs réseau
ou disque, le maintien d'une manœuvre en attente et le rafraîchissement de la TUI.

Le 9 octobre 2026, six échanges avec `gpt-6.1-sol` via le forfait ont été relus :

- Arrivée : récit du passage par l’échoppe de Gorm.
- Relance « pourquoi il ne va pas le chercher lui-même ? » : résolution du pronom, sans inventer ses raisons.
- Visibilité sans fenêtres : explication par la lanterne et la lueur de l’ouest.
- Extraction au couteau : proposition validée pour l’axe supérieur, DD 18.
- « Donc je l’ai retiré ? » : distinction entre proposition et réussite, porte toujours fermée.
- Après extinction effective de la lanterne : pénombre, silhouettes visibles mais détails illisibles.

Les temps observés étaient de 3,7 à 5,4 secondes par réponse. Cet échantillon n’est pas une
preuve de fidélité générale : les tests automatiques contrôlent surtout le contrat, la mémoire,
la séparation dialogue/action et la conservation de l’état. La prose se vérifie aussi en jouant.

Référence d'intégration : [appels de fonction de l'API OpenAI](https://developers.openai.com/api/docs/guides/function-calling).
Connexion forfait : [inscription et connexion](https://developers.openai.com/siwc/token-sharing-open-source/sign-in),
[requêtes d'inférence](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference),
[contraintes du flux](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations).

Les tests TUI utilisent le pilote clavier de Textual, hors réseau : prise et dépôt de la clé,
rafraîchissement des vues, boutons de confirmation, redimensionnement, historique de saisie
et maintien de l’interface pendant un appel simulé du MJ. Sans Textual, ces tests sont ignorés.
`tools/apercu_tui.py` exporte des captures SVG à plusieurs tailles, dans `artifacts/tui`,
sans modifier la sauvegarde utilisateur.

Références TUI : [tests Textual](https://textual.textualize.io/guide/testing/),
[workers et threads](https://textual.textualize.io/guide/workers/).
Copie : [sélection de texte Textual](https://textual.textualize.io/FAQ/#how-can-i-select-and-copy-text-in-a-textual-app),
[presse-papiers Pyperclip](https://pyperclip.readthedocs.io/en/latest/).
