# Relations graduées — sous-étape 3b

Branche `codex-relations-3b`, dans `tmp-worktrees/codex-relations-3b`, issue de
`06602a6` (`main` lors de l'ouverture). Travail non fusionné ; `main` n'a pas été modifié.

## Règles et responsabilités

`donjon/relations.py` porte seul les cinq axes orientés, les seuils et les causes.
Un étranger vaut 40 en confiance et zéro ailleurs. Les profils déclarent `liens` ;
les scénarios déclarent séparément les voix déjà connues. Le joueur n'a pas de relations
propres ; chaque PNJ peut en avoir une envers lui. `fiable` reste un mot de la parole,
mais quitte les croyances persistantes. Aucun changement de modèle, de consignes ni de
schéma de proposition du MJ.

`esprits.memoriser` inscrit le souvenir puis appelle le crochet unique
`relations.souvenir`. La table `EPREUVES` applique les variations du plan, modulées par
fierté, loyauté, empathie, courage et honnêteté. Les trois derniers motifs sont conservés
avec leurs variations effectives. Un refus technique n'est pas un affront ; un achat
n'est pas un don ; la restitution d'un prêt n'est pas un nouveau cadeau.
Le compteur `vols_surpris` demeure distinct et conserve le refus des ventes.
Les causes de refus par rancune et par méfiance sont distinctes. Les retours de parole
décrivent l'avis ou l'aveu retenu, le mensonge constaté ou le prêt reproché ; ils n'annoncent
plus une rupture totale de confiance quand l'axe n'a subi qu'une variation partielle.

L'estompement est calculé sans écrire lors des lectures : affection vers le lien de
départ à un point par heure ; rancune à demi-vie `720 × fierté / 50 / (1 + douceur / 100)`
minutes ; peur à demi-vie 120 minutes. Des ancres exactes par axe évitent qu'un autre
événement ou des rechargements répétés effacent les fractions de temps. Les axes exposés
restent entiers. Confiance et dette ne s'estompent pas. Bandes : méfiance <30/sortie40,
confiance ≥60/sortie<50, rancune et peur ≥40/sortie<30.

Une identité seulement prétendue n'emprunte jamais la confiance du personnage nommé.
Un événement partagé entre constat, attribution à l'oreille et rumeur conserve une preuve
durable. On ne sanctionne pas deux fois le même fait après éviction des quarante souvenirs ;
une preuve plus forte ne produit que le complément. Le suivi des portages évite de
redécouvrir sans cesse le même vol. Une promesse accomplie hors de vue n'est apprise par
son bénéficiaire qu'à réception du service ou par une annonce effectivement entendue dans
un échange ; la simple présence de son auteur ne transmet pas ce savoir.

Les dettes morales diminuent quand le débiteur accepte une demande ou rend effectivement
un service. La même demande ne solde pas une seconde fois la dette lors de sa réalisation.
La compagnie dans l'épreuve s'accumule à la minute perçue, persiste à la reprise et inclut
le joueur. Le compteur ne dépend pas du nombre de consultations.

## Lectures et outils

La persuasion emploie la formule graduée du plan, VOL comprise. Demandes, appels,
passages, écoute, compagnie et choix d'un proche lisent les axes. La mémoire des recherches
du planificateur inclut axes et bandes ; le coût d'une présence crainte utilise sa position
crue, y compris celle du joueur. Les liens contrastés de la crue sont des données de profil.

Le récit présente les changements de bande et leurs causes, puis les motifs et relations
de fin de nuit. L'observateur relève aussi les transitions dues à l'estompement. Le rejeu
conserve les axes et motifs dans le temps. Les six nouvelles mesures sont présentes ;
l'ancien nombre de créances matérielles, précédemment nommé `dettes`, s'appelle désormais
`dettes_materielles` pour le distinguer des dettes morales de fin de nuit.
Le comptage commun de `banc_pnj.executer` relève les bandes au départ et à chaque pas,
puis les unit aux transitions de la chronique. Il inclut ainsi l'estompement pur, avec ou
sans récit ; un test contrôle peur et rancune, monde identique et texte après rechargement.

| Fonctions | Responsabilité |
|---|---|
| `relations.installer`, `verifier` | Liens d'auteur et contrat persistant de l'esprit |
| `identifier`, `souvenir`, `_appliquer`, `EPREUVES` | Preuve stable, attribution et effets des souvenirs |
| `_lecture`, `_estompes`, `envers`, `axes`, `percue` | Lectures pures, estompement, identité perçue |
| `partager`, `annoncer_suites` | Minutes perçues dans l'épreuve et transmission effective des engagements |
| `planification._entrees`, `Vue.pression` | Invalidation des recherches et coût de la peur |
| `Recit`, `Enregistreur`, `banc_pnj.executer` | Récit, rejeu et mesures communes |

## Vérifications

Les tests dédiés passent par sauvegarde/rechargement et contrôlent aussi le récit, les
paroles visibles, le contexte reçu par le MJ ou le rejeu. Ils comprennent :

- crue : Brune donne du bois puis prévient réellement Gorm d'un vol vu ; confiance
  20 → 30 (méfiance maintenue) → 45 (levée) ; la demande suivante atteint le jet ;
- mine : Odon refusé par Mathe conserve le motif ; Mathe le voit manger le pain de Lucien
  et s'en méfie ; autre couple pour les refus et torts ;
- joueur surpris : rendre chacun de deux objets augmente la confiance sans effacer le
  souvenir du vol ni rétablir les ventes ;
- prêts, restitution par l'emprunteur et reprise par le propriétaire, don et achat ;
- calcul des axes et modulations, hystérésis, lectures pures, estompement fractionnaire
  malgré d'autres événements, voix inconnues, preuves répétées ou renforcées ;
- engagement tenu ou abandonné hors de vue, reprise puis annonce entendue et affichée ;
- dette soldée une fois, compagnie perçue pendant une heure malgré reprise au milieu,
  et absence de cumul lors de deux consultations de la même minute ;
- affection 49/50 et orgueil au passage, confidence au plus aimé et égalité par identifiant,
  abri du plus aimé avec arrivée effective ;
- peur ou rancune seules à 59/60 pour les appels, refus de passage et d'échange malgré une
  confiance intacte, surveillance du bruit par peur ; coût et mémoire des recherches après
  changement de peur puis estompement, à croyances physiques constantes.

Les anciennes scènes qui écrivaient `fiable` déclarent maintenant un lien chiffré. Trois
états archivés de tests ont été convertis comme données d'auteur ; aucune migration de
sauvegarde ancienne n'a été ajoutée au jeu.
Les tests de nuits libres qui présupposaient un acheteur ou un voleur précis ont été
adaptés à leurs conséquences réelles, ou remplacés par une scène physique déterminée.
Ainsi, crue 7 : après refus, Brune prend les planches d'Aubin pour le poêle ; les trois
charges de bois du guet restent intactes et une seule planche est consommée, après reprise.
À l'auberge 1985, départ fixe, tranche 100 → 210 : les événements distincts passent de
11 à 9 et les échanges de 8 à 6. Les deux événements absents sont « Lucien appelle à
l'aide » et « Lucien reste dans la lumière » ; aucun événement nouveau dans cette tranche.
Le test conserve un plancher de diversité, six acteurs, les échanges et surtout l'identité
complète de la suite de nuit après reprise. La scène du palier déclare désormais son but
d'abri en cours au lieu de l'hériter d'une nuit préparatoire devenue différente ; les bornes
de passages et l'interdiction de retour vers la galerie restent inchangées.
Autre conséquence de cette nuit d'auberge : à 300, l'âtre et le fourneau brûlent encore,
mais le poêle d'Anselme est éteint. Odile a refusé ses bûches de réserve, dont huit charges
restent chez elle ; ce n'est pas une pénurie globale de bois. Après sa remise acceptée et
du bois reçu de Mireille, les trois foyers brûlent à 420 ; la réserve compte encore cinq
charges. L'ancien résultat « trois foyers à la cinquième heure » n'est donc plus garanti
par cette nuit libre. Le test conserve les refus/remises, les charges et les feux à chaque reprise.
La scène d'Ilse au refuge contrôle aussi que « reste en compagnie » est affiché lorsqu'Aubin
est dans sa salle mais à plus d'une case ; les autres scènes contrôlent le vrai rapprochement
du compagnon le plus aimé.
Un dernier audit dirigé a reproduit un autre écart de rendu : derrière Ilse, Aubin est à
deux cases, tandis qu'elle le croit encore à une case. Le déplacement demeure fondé sur
cette croyance, mais le texte du moteur ne doit pas en faire un fait physique. `_abriter`
vérifie maintenant la distance réelle parmi les compagnons perçus avant de dire « près ».
Le même parcours complet, après recharge, passe aussi avec Brune et Gorm ; les vingt tests
ciblés des lectures, de la sécurité et de l'abri sont verts.
Le banc libre confirme cinq lignes de chronique corrigées sur quatre nuits : Relais 500,
minute 191 (Gorm près d'Ilse plutôt que d'Aubin) ; crue 1985, minute 129 (Gorm près d'Aubin,
Ilse près de Gorm) ; crue 7, minute 106 (Ilse près de Gorm) ; crue 2024, minute 330 (Aubin près
de Gorm). Les empreintes, souvenirs et autres mesures sont identiques sur les vingt nuits.
Seuls deux comptes d'événements distincts, fondés sur les textes, changent : 38 → 39 au
Relais 500, 36 → 35 à la crue 1985. Aucune règle de décision n'est modifiée par ce rendu.

## Protocole des bancs

Sans appels au modèle, départ tiré, nuits de huit heures, priorité réduite, au plus quatre
processus. Série de référence exécutée avant la série de branche. Relais : graines
1985, 7, 42, 2024, 3, 11, 99, 500 ; mine, auberge et crue : 1985, 7, 42, 2024.
Joueur passif à `chambre_cloche` (Relais/crue), `galerie` (mine), `dortoir` (auberge).
Quatre nuits supplémentaires, graine42, activent `planification.VERIFIER` et
`spatial.VERIFICATION = 0.2`.
Après la suite finale, une dernière paire complète référence puis branche est exécutée
sans autre calcul lourd de ce chantier, pour rapprocher les conditions de chronométrage.

La vérification de la priorité réelle a révélé que l'ancien appel Windows de `ceder`
tronquait le pseudo-handle 64 bits : son échec laissait le processus en priorité normale.
La branche passe un pointeur explicite ; la référence est remesurée via une enveloppe
équivalente, sans modification de `main`, en priorité réellement réduite.

Les nuits sont mesurées à caches de recherche vides, quel que soit leur worker. Le dernier
réglage de performance calcule une seule fois les peurs dans une `Vue` immuable ; les
positions crues continuent d'être rejouées à chaque état. Les sorties de cette optimisation
sont comparées intégralement aux nuits précédentes, hors temps de calcul.

## Résultats et verdict

Moyennes par nuit, référence → branche. Les nombres de dettes morales et de créances
matérielles ne sont pas comparés comme s'il s'agissait de la même mesure.

| Scénario | Échanges | Vols vus | Rumeurs crues | Méfiances en fin de nuit | Minutes urgentes sans recours |
|---|---:|---:|---:|---:|---:|
| Relais (8) | 18,25 → 16,125 | 1 → 0,875 | 0,75 → 0,625 | 2,25 → 1,625 | 70 → 58,75 |
| Mine (4) | 42,25 → 43,75 | 0,25 → 0,5 | 0,5 → 1,5 | 3,75 → 3,75 | 37,5 → 13,75 |
| Auberge (4) | 29,25 → 29,25 | 0,75 → 1,25 | 4 → 3 | 7,25 → 4 | 138,75 → 96,25 |
| Crue (4) | 14,25 → 15,75 | 0 → 1,5 | 0 → 2,5 | 0 → 2,5 | 23,75 → 105 |

Les méfiances de départ de la crue sont désormais déclarées, d'où une différence attendue
avec le zéro de référence. « Rumeurs crues » compte les souvenirs conservés en fin de nuit,
comme avant ce chantier ; ce n'est pas le total des paroles prononcées.

Les mesures suivantes sont nouvelles : seule la branche est renseignée.

| Scénario | Méfiances levées | Rancunes ≥40 | Dettes ≥20 | Dettes honorées par demande | Paires ayant changé de bande |
|---|---:|---:|---:|---:|---:|
| Relais | 0 | 0,5 | 1,625 | 0,625 | 2,375 |
| Mine | 0 | 0 | 4,25 | 0 | 2 |
| Auberge | 0,25 | 0,5 | 5 | 1,75 | 4,25 |
| Crue | 0 | 0,75 | 2 | 0,25 | 2,75 |

**Critère global de 3b non atteint.** À l'auberge, une nuit sur quatre lève une méfiance
par un service : graine 7, minute 157, Odile ouvre le garde-manger et sert le repas promis à
Joss ; `engagement_tenu` le fait sortir de la méfiance, avec sa cause dans la chronique et
le rejeu. À la crue : zéro sur quatre. Les cas dirigés montrent que rendre le service puis
prévenir fonctionne, mais les PNJ n'ont pas encore de but pour réparer volontairement leur
relation (3e). Une capacité démontrée en scène ne remplace pas le critère des nuits libres.

Le surplus de minutes sans recours est propre à la crue (+342 %). Le récit permet de le
suivre : la méfiance initiale de Gorm bloque la demande de Brune dès la première minute ;
en référence elle était nourrie aussitôt (don en 1985, achats aux autres graines). Après
trente minutes de guet, elle renonce puis attend le répit générique de soixante minutes.
Les comptes à la minute du récit pour Brune sont 0 → 59 (1985), 0 → 119 (7), 36 → 177 (42),
59 → 59 (2024) ; Aubin ajoute une minute en 7. Les mesures du banc, relevées par pas de cinq
minutes, peuvent différer de quelques minutes des comptes à la minute du récit.
Renoncements/reprises : 33/93 (1985), 34/94 et 380/440 (7), 34/94, froid 253/313 puis faim
379/439 (42), 33/93 (2024). Cet écart est expliqué, sans faire disparaître l'attente par un
traitement propre à Brune ou à Gorm.

| Scénario | Secondes référence → branche | Écart |
|---|---:|---:|
| Relais | 11,20375 → 11,84625 | +5,73 % |
| Mine | 34,165 → 30,5625 | −10,54 % |
| Auberge | 25,5825 → 29,575 | **+15,61 %** |
| Crue | 13,09 → 22,45 | **+71,50 %** |

**La borne de temps +10 % échoue à l'auberge et à la crue.** Ce tableau utilise la dernière
paire rapprochée, référence puis branche, après l'arrêt de tous les autres calculs lourds
de ce chantier. Les premières séries variaient fortement avec la charge du poste ; leurs
comparaisons de temps ne sont pas retenues pour le verdict. Les sorties de chaque source
restent intégralement identiques hors secondes à leur série précédente : vingt nuits de
référence et vingt de branche, sans réglage entre les deux. Le précalcul des peurs dans
`Vue` réduit un coût commun et conserve le comportement, mais ces deux dépassements restent
à corriger. Ils ne sont pas assimilés à un critère atteint parce que leur cause est plausible.

Les quatre nuits finales de huit heures, graine 42, avec `VERIFIER` et contrôle spatial
0,2 sont sans écart, borne ni plantage. Leurs chroniques, toutes leurs mesures et toutes
leurs empreintes sont identiques aux nuits normales correspondantes. Priorité réduite
effective vérifiée pour les quarante exécutions de la paire et les quatre contrôles,
fichiers de production identiques en début et fin
de chaque lot. Aucune usurpation ni violation du monde dans les vingt nuits normales.
Les captures comptent 30/23/30/30 preuves durables en fin de nuit (Relais/mine/auberge/crue).
Une suite reste à annoncer à l'auberge : Joss a allumé le fourneau pour Mireille à 439,
qui ne l'a pas encore appris ; aucune relation ne lui est modifiée par cette seule réussite
lointaine. Les trois autres scénarios n'ont pas de suite en attente.

Suite complète verte après le dernier correctif : **1311 tests, zéro échec, zéro erreur,
14 ignorés** (1297 réussis), en 382,162 s, répartis sur quatre workers en priorité réduite.
Le lanceur local utilise la découverte `unittest` complète et conserve exactement ses
1311 identifiants, y compris les classes réexportées par certains modules ; il n'écarte
aucun module. Les 14 ignorés dépendent du support MiMo facultatif absent de cet environnement.
Les vingt tests ciblés de proximité/abri et les trois tests de ressources/compagnie passent
aussi séparément. Le contrôle Node exécute la page de rejeu et vérifie que ses panneaux
affichent réellement les cinq axes.
La commande habituelle de reproduction depuis ce worktree utilise le Python du dépôt
principal : `..\..\.venv\Scripts\python.exe -m unittest discover -s tests -q`.

Les preuves locales sont dans `artifacts/relations-3b/` (non versionné) : `base-rapprochee/`,
`branche-rapprochee/`, `comparaison-rapprochee.json`, `preuve-base-rapprochee.json`,
`preuve-branche-rapprochee.json`, `preuve-proximite.json`, `preuve-optimisation.json`, `verification-proximite/`,
`tests-suite-proximite.log`, `tests-proximite-finale.log` et `tests-ressources-compagnie-final.log`.
Les empreintes des vingt nuits de la branche sont distinctes de la
référence : les comportements changent comme attendu ; seules les deux versions de
l'optimisation sont comparées pour identité de comportement.

## Réglages proposés

- Garder les seuils et les variations de la table pour cette première mesure : changer les
  liens pour forcer une levée de méfiance masquerait l'absence de service spontané en 3b.
- Étudier séparément le coût commun des recherches répétées après un refus et pendant un
  répit. À la crue, les recherches passent de 1054,75 à 2931,25 par nuit, les recherches neuves
  de 520,25 à 830,75, les gestes seulement de 218,75 à 237,25. Il faut réduire le travail
  équivalent sans réutiliser un plan lorsque les axes ou les positions crues ont changé.
  Le surcoût de l'auberge n'a pas été isolé par un profilage comparatif ; il reste à mesurer
  avant de choisir une optimisation. Le verdict de temps demeure négatif sur ces deux scénarios.
- Mesurer de nouveau le critère des services avec les propositions et réparations de 3e ;
  ne pas avancer cette sous-étape sous forme d'une exception de scénario.

## Limites conservées

- Aucun signe, émotion nouvelle, empathie décisionnelle, proposition ni avis spontané
  des sous-étapes 3c à 3f. L'humeur et son rendu existants restent en place jusqu'à 3c.
- Une opinion positive seule ne regagne pas la confiance ; il faut un événement probant.
- Le registre durable des preuves croît avec les incidents distincts ; il n'est pas borné
  aux quarante souvenirs. Ce choix garantit la non-répétition après oubli et recharge.
- La compagnie partagée est un cumul des minutes observées par le filet de délibération,
  pas une intégration continue à la seconde.
- Une nouvelle déjà connue est refusée par `social.recevoir` tant que son souvenir subsiste.
  Le crochet sait compléter une preuve renforcée (vu après entendu, ou variation de source),
  mais la corroboration d'une rumeur par une seconde source ne traverse pas ce garde-fou.
  Le test contrôle explicitement cette limite du circuit réel puis le contrat du crochet ;
  il ne prouve pas une réévaluation sociale active.
- La validation des contradictions mécaniques dans une narration libre demeure en partie
  sémantique, conformément au contrat du dépôt ; ce chantier ne la prétend pas résolue.
