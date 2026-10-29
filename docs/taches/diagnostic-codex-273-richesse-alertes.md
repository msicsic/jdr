# Diagnostic complémentaire du lot 273 — richesse de la mine et alertes

29 octobre 2026. Relecture des quarante nuits déjà archivées de
`0e3e626` et `527b505` ; fonction `cats` du lot 183 inchangée. Aucun banc
comparatif ni suite de tests relancé. Moteur inchangé.

**Verdict avant fusion : défaut du correctif établi.** La conservation de
la demande est nécessaire, mais sa continuation confond encore le moyen
initial avec le résultat à poursuivre. Une part effectivement acquise et
reconnue par un reçu est traitée comme une autre demande. Le recul ne peut
pas être déclaré légitime. Toutes les signatures perdues ne sont cependant
pas des actions supprimées : des refus deviennent des accords, des auteurs
et des bénéficiaires changent, et des trajectoires divergent en aval.

## Signatures exactes perdues et gagnées

S compte `(famille, auteur, texte exact)`, pas les interactions causales.
Un changement `necessaire` → `promis` compte une perte et un gain. Les
services sont attribués à leur auteur, conformément au lot 183.

| Graine mine | S référence → branche | Perdues | Gagnées | Solde |
|---|---:|---:|---:|---:|
| 1985 | 32 → 12 | 24 | 4 | −20 |
| 7 | 19 → 18 | 6 | 5 | −1 |
| 42 | 24 → 13 | 18 | 7 | −11 |
| 2024 | 28 → 18 | 16 | 6 | −10 |
| Total | 103 → 61 | 64 | 22 | −42 |

| Famille | Signatures perdues | Gagnées |
|---|---:|---:|
| Demande | 29 | 7 |
| Offre matérielle | 17 | 4 |
| Appel (inclut « appelle et donne une part ») | 7 | 5 |
| Service crédité | 8 | 4 |
| Interposition | 3 | 1 |
| Promesse en contrepartie | 0 | 1 |

Familles qui **disparaissent entièrement pour un PNJ dans la nuit** :

| Graine | Familles × auteurs perdues | Familles × auteurs nouvelles |
|---|---|---|
| 1985 | Demande : Mathe, Odon ; offre : Gaspard, Josse, Mathe ; appel : Bram, Lucien, Rémy ; service : Lucien, Mathe, Rémy ; interposition : Rémy | Service : Josse |
| 7 | Offre : Gaspard ; service : Mathe | Appel : Bram, Josse ; service : Josse |
| 42 | Appel : Josse ; demande : Lucien ; offre : Josse, Lucien, Rémy ; service : Josse, Mathe ; interposition : Rémy | Demande : Mathe, Odon ; offre : Mathe ; promesse : Josse ; interposition : Bram |
| 2024 | Demande : Mathe ; offre : Josse, Mathe ; service : Rémy ; interposition : Rémy | Appel : Bram ; offre : Rémy ; service : Bram, Josse |

Soit 27 couples famille/PNJ perdus, 13 nouveaux : le solde −14 explique
exactement D −0,5 en moyenne sur quatre nuits et sept PNJ. Les crédits de
service effectivement racontés passent aussi de **8 à 4**, répartis
**3/1/3/1 → 1/1/0/2** dans l'ordre des graines. Le phénomène n'est donc
pas seulement lexical. Exemples : le service Josse→Odon à `373` disparaît
en 42 ; en 1985 le service Mathe→Odon à `18817` est remplacé par
Josse→Odon à `18627`, tandis que Rémy→Lucien et Lucien→Gaspard disparaissent.
Les 86 lignes de signatures perdues/gagnées par nuit, avec leurs occurrences,
instants et auteurs, sont détaillées
dans `diagnostic-richesse-alertes.json`.

**Une partie du recul est légitime ou liée au compteur.** En mine 42,
Mathe nourrit Gaspard dans les deux versions : à `4365` puis `4665` en
référence (« appelle et donne », crédit spontané au premier service),
à `4406` en branche après sa promesse à `4321` (« donne une part »,
prestation convenue sans crédit spontané). Les signatures appel/service
disparaissent donc sans disparition du repas. En 1985, le refus de Mathe à
Gaspard devient aussi une promesse (`70961`), effectivement servie à
`71220`, ce qui remplace des démarches et dons d'autres PNJ. **8→4 crédits
ne signifie pas 8→4 repas.** Ce sont des changements concrets de régime
d'échange ; ils ne permettent ni de condamner les 42 signatures nettes,
ni d'excuser le défaut de continuation démontré ci-dessous.

## Première divergence attribuable, puis défaut reproductible

Mine 1985 rejouée depuis le départ tiré, joueur en galerie, dans les deux
versions isolées. Arrêt au premier choix affecté, **`268` dixièmes (26,8 s)**.
Les deux mondes **avant choix sont exactement égaux**, pas seulement leurs
buts ou leur rendu. Josse veut servir Odon depuis le lot `biscuits` ; Bram
vient de refuser gratuitement et de proposer une part à une pièce.

La référence efface l'intention puis suit le recours d'achat à une pièce,
qui fait **servir Josse**. La branche conserve la demande de servir Odon
et prépare une **part à remettre** à trois pièces. Les modes de livraison
diffèrent : le seul prix 1→3 ne prouve donc pas un surcoût injustifié pour
un effet identique. Cette première divergence explique déjà la distribution
des ressources et les signatures suivantes ; elle ne suffit pas au verdict.

Le défaut est établi à **`373` (37,3 s)**, après livraison réelle :

- Josse porte `biscuits_1`, en est propriétaire, avec une portion ; le reçu
  publié contient `objet=biscuits_1`, `lot=biscuits` et `livraison=true`.
- Odon est perçu dans la même salle, encore affamé. `_fin_demande` ne
  certifie aucune fin. Le planificateur produit le moyen admissible
  `servir biscuits_1 pour odon`, sans autre acquisition ni déplacement.
- La demande adoptée reste liée à `objet=biscuits`. Le moyen reçu est
  rejeté comme autre demande par `_meme_demande_adoptee`. Son urgence
  identique (**palier 12, valeur 20**) ne domine pas l'active : Josse
  **redemande le lot à Bram** au lieu d'employer sa portion.
- L'archive confirme un refus supplémentaire à `600`, puis le maintien du
  but source jusqu'à `18000`. Josse n'emploie finalement la portion pour
  Odon qu'à `18627`, après changement de but et retour du bénéficiaire.

Contre-épreuve sur copie de la capture : exécuter le seul service déjà
produit par le planificateur réussit, fait passer la faim d'Odon de
**85,077 à 35,077**, et publie le service Josse→Odon. Aucune ressource,
relation ou croyance favorable ajoutée. Les captures avant/après des deux
choix à 268, du choix à 373 et du service contrefactuel passent **21
égalités monde/rendu/scène après sauvegarde et recharge**. Bruts :
`richesse-mine-reference/`, `richesse-mine-premiere/`,
`richesse-mine-part-recue/`, `preuve-part-recue.json`.

**Attribution.** C'est une frontière manquante du contrat commun, exposée
par le 273 : le lot source est un moyen d'acquisition, pas l'identité
permanente de la part finalement reçue. L'ancien abandon pouvait masquer
cette lacune en recréant ultérieurement un secours visant la nouvelle
entité. Les anciennes scènes de repas sur nourriture déjà portée ne
couvraient pas cette transition. La causalité de chaque différence des
quatre nuits n'a pas été prouvée par contre-épreuve ; le défaut suffit à
interdire de classer globalement le recul comme légitime.

## Correction proposée, non implémentée

Séparer l'identité durable de la demande et les liaisons de ses moyens.
Lorsqu'un préfixe produit une entité concrète — fractionnement, remise ou
transformation — la continuation doit exploiter la provenance **publiée et
validée**, ici le reçu existant `lot → part`, pour revalider la suite de la
même demande. Aucun nouvel objectif, aucun nouvel impératif d'urgence ni
critère de naissance relancé. Un prix négocié doit aussi être évalué avec
son véritable effet et son mode de livraison.

Une liaison acquise doit rester attachée au contrat actif et survivre à
la sauvegarde et à l'éviction des souvenirs bornés ; retrouver le reçu
dans les quarante derniers événements à chaque reprise ne suffirait pas.

Ne pas remplacer cette règle par « même raison = même demande » : une
mission peut exiger un bien précis. Les substitutions admissibles doivent
être déterminées par le contrat et la provenance, jamais par une liste
d'objets ou une instruction au MJ. Refus, droits, présence, quantités,
préemptions et sauvegarde restent les contrôles communs. La validation doit
inclure la capture 373, le cas Aubin 117503 et une autre acquisition
différée, hors perception, avec reprise après recharge et laps découpés.

## Hausses d'entrées « à expliquer »

Ces classes ne sont pas des suspects 219 certifiés. L'archive permet les
constats suivants ; aucun classement du compteur n'a été changé.

| Nuit | Analyse des retours |
|---|---|
| Crue 7, 0→2 | Gorm attend Aubin à `23079` après nouveau dialogue d'appel (`23059`), alors que le premier rendez-vous est clos par « retrouve Aubin » à `3448` : nouveau rendez-vous réel, pas une répétition sans fait. Le brasero revient à `104400` après évacuation de Brune, constat brasero éteint/épuisé et acquisition du bois du guet à `104037` ; des moyens et l'état ont changé. Aucun réessai par le seul délai démontré ; nécessité exacte du choix non contrefactuellement certifiée. |
| Crue 2024, 1→2 | L'ancienne alerte d'agenda de Brune disparaît. Deux retours de garde de Gorm apparaissent : `45366` après abri, appel/venue d'Aubin, prévention et bruits ; `127930` après enquête chaleur, entretien tenté, inspection et fermeture de réserve. Changements de sécurité, présences, eau et ressources documentés ; retours après d'autres recours, pas identité des entrées. Attribution de leur classement au seul 273 non établie. |
| Hameau 42, 2→4 | Les retours d'abri Brune/Maël à `81000` sont **identiques dans la référence**, pas nouveaux. Les ajouts sont l'agenda a1 de Brune (`81600→81622`, sommeil puis offre à Aubin) et l'interposition de Gorm (`94840→94880`, cible Aubin→réserve→ronde→Aubin). Le rejeu ci-dessous confirme une entrée perceptive et une préemption pour Gorm. Pour Brune, le devis passe de `None` à une offre admissible, sans nouvel interlocuteur perçu ; la cause nécessaire du changement de devis n'est pas isolée. |
| Hameau 2024, 0→1 | Brune revient au froid à `64200` lorsque son agenda d'argent passe en sommeil, après offres refusées à Ilse/Maël. Froid resté pressant (70,2→70,3), clé réellement prise à `63630`, puis trajet au poêle : reprise corporelle après épuisement d'un autre recours, conforme à la raison modélisée. Pas de défaut 273 démontré par ce retour. |

Les mouvements, changements d'eau, nouvelles ressources ou interlocuteurs
ne suffisent pas à eux seuls à prouver la nécessité de chaque choix.
L'analyse ci-dessus distingue les événements attestés de leur attribution
causale ; elle ne transforme pas les sept retours ajoutés en innocuité
universelle.

**Rejeu ciblé du hameau 42**, arrêté à `94880`, **34,031 s**, sans rejouer
la fin de nuit : dix captures, **30 égalités monde/rendu/scène après
recharge**. À `94865`, Gorm voit la réserve mais plus Brune et abandonne
l'interposition impossible ; à `94880`, il revoit Brune/Ilse/Maël,
la position crue d'Aubin a changé (`[5,4]→[5,3]`) et l'interposition
préempte la ronde **13→5**. Ce retour est justifié par la perception et
le contrat de priorité ; le compteur ne voit pas tout ce contenu.

Brune perçoit exactement les mêmes entités et cases à `81600` et `81622`.
Les changements enregistrés comprennent l'eau crue de l'échoppe 21→22 et
une garde entendue de Gorm. Revenir séparément sur ces deux changements ne
supprime pas l'offre à Aubin : ils ne sont pas des preuves suffisantes de
nécessité. Cette alerte reste donc ouverte plutôt que certifiée bénigne.

Contrôle de l'attribution : chargées dans **l'ancien et le nouveau moteur**,
les mêmes trois captures avant choix (`81600`, `81622`, `94880`) produisent
**les mêmes états complets**, SHA-256 égaux. La condition d'effacement du
plan démenti d'une demande typée n'est satisfaite sur aucun de ces choix. Les alertes sont donc
exposées par une autre trajectoire, sans nouvelle divergence locale de
l'arbitrage démontrée. Ce contrôle ne tranche pas la correction générale
du devis de marché. Bruts : `alertes-hameau42/`, `choix-alertes-*.json`,
`constat-alertes-hameau.json`. **Fusion à différer**, en raison du défaut
lot→part établi indépendamment de ces alertes.

## Bilan du banc conservé

Ordre des graines : 1985 / 7 / 42 / 2024. Aucune hausse des suspects 219
sur les vingt paires ; total 1→0, seul suspect de référence Aubin Relais
2024 à `117518`, absent en branche. Sa trajectoire entière a changé ; la
conservation isolée de sa demande est contrôlée par la capture `117503`.
S/F/D : moyennes des quatre nuits, PNJ inactifs compris.

| Scénario | 219 par nuit, référence → branche | S/F/D, référence → branche |
|---|---|---|
| Relais | 0/0/0/1 → 0/0/0/0 | 15,25/4,25/1,750 → 15/4,25/1,625 |
| Mine | 0/0/0/0 → 0/0/0/0 | 25,75/5/1,964 → 15,25/5/1,464 |
| Auberge | 0/0/0/0 → 0/0/0/0 | 9,25/4/1 → 9,25/4,25/1,031 |
| Crue | 0/0/0/0 → 0/0/0/0 | 23,50/6,75/3,063 → 27/6,75/3,250 |
| Hameau | 0/0/0/0 → 0/0/0/0 | 22,75/7,25/2,167 → 24,75/7,25/2,208 |

Zéro plantage, usurpation ou violation d'audit. Deux observations nouvelles
`voir_alterne` de Gorm, Relais/crue 2024 à 5 min ; deux bascules en crue
2024, sous le seuil 10. « À expliquer » 21→18 ; dérives ouvertes 203→205,
cycles 503→483, préemptions 49→62. Pertes de service 4→4 : cessation
physique 3→4, bénéficiaire parti 1→0, aucune violation de service.
Attente urgente 695→375 PNJ·min, sans recours 0→0. Le recul de richesse à
la mine (S −40,8 %, D −25,5 %, F stable) ne se trouve pas annulé par ces
autres indicateurs. Le critère 219 reste tenu ; l'aptitude à la fusion
est refusée sur la preuve de continuation défaillante décrite plus haut.
