# Menace ou échéance négociée — conception du lot 347

30 octobre 2026. Proposition à arbitrer, documentation seule ; aucune mécanique nouvelle livrée.
Branche `codex-conception-menace`, base `origin/integration 368bf6c`, vérifiée sur origin.
La référence locale `integration` est ancienne ; elle n'est pas la base de ce lot.
Le contrat de référence est [AGENTS.md](../AGENTS.md). Les mentions anciennes
« non fusionnée » des plans ne suffisent pas à décrire cette base : l'inventaire ci-dessous
repose aussi sur le code présent. Aucun résultat ancien n'a été rejoué.

**Recommandation : l'échéance négociée d'abord**, sur une livraison ou une tâche ponctuelle
déjà admise par le moteur. Premier enjeu : « Je paie cette prestation maintenant, à condition
qu'elle soit faite avant telle date de jeu ». Le joueur peut proposer un autre délai ou
renoncer ; un PNJ peut refuser un délai qu'il ne pense pas pouvoir tenir. La menace apporterait
une stratégie plus différente de l'échange, mais il lui manque encore le jugement d'une
sanction annoncée, sa portée sur les refus sociaux et les suites de la contrainte.

Le premier périmètre ne couvre pas tout contrat temporel : prêter jusqu'à une date, maintenir
un état pendant une durée et payer plus tard ont des obligations différentes. Leur absence doit
être annoncée dans l'interface et dans la compilation, sans supprimer une clause de la saisie.

## 1. Quatre cas de jeu et leurs sources

Les événements archivés ci-dessous sont des observations historiques, pas des trajectoires
garanties sur la base actuelle. Les phrases proposées sont les choix que la mécanique ouvrirait ;
elles n'ont pas été jouées. Les cas issus des seules données sont signalés comme tels.

### 1.1 Crue : récupérer les planches sans devoir commencer par un coup

**Source directement relue :** [capture crue 2024, minute 680](../tests/data/crue-2024-680.json.gz),
chronique et objets, décompressés en lecture seule. À 459, Aubin dit à Ilse que Brune porte les
planches qui ne sont pas à elle. À 680, `planches` est porté par Brune et appartient à Aubin.
La torche appartient à Brune : il ne faut pas assimiler les deux conflits de possession.
La même archive contient à 633 un coup d'Aubin sur Ilse et une intervention de Gorm contre Aubin ;
elle ne prouve ni une menace préalable ni une agression de Brune dans cet épisode.
Le [rapport 155](taches/rapport-codex-155-fuite-lumiere.md) documente les recours de fuite et de
lumière de cette famille de scènes ; ses chiffres décrivent sa version historique.

**Aujourd'hui.** Le moteur sait représenter propriété, portage illégitime connu, récupération,
demande, refus, violence et secours. Il ne dispose pas d'un acte général « menacer de… si… ».
Un propos menaçant peut être retenu sans que son alternative soit jugée ; demander puis frapper
reste une succession d'actions, sans équivalent systémique de la dissuasion annoncée.

**Ce qui manque.** Comparer pour Brune restituer, refuser, s'éloigner ou demander secours face à
une sanction qu'elle croit possible. Le portage connu des planches n'autorise pas le moteur à
connaître la résolution secrète d'Aubin ni à imposer la restitution.

**Choix joueur.** Intervenir : « Rends les planches à Aubin ou je te frappe », soutenir une
demande pacifique, protéger Brune ou se retirer. La première phrase doit enregistrer une menace
entendue ; elle ne frappe personne, ne transfère rien et ne prouve aucune culpabilité nouvelle.
La réalisation ultérieure de la sanction reste un autre acte, revalidé et confirmé si nécessaire.

### 1.2 Auberge : acheter une livraison à temps pour rallumer une lanterne

**Source historique :** [rapport 3, de l'huile pour une lampe](taches/rapport-codex-3-lampes.md),
section « Mesures » : auberge 1985, achat d'Anselme à Joss à 528, puis à Odile à 618,
livraison et recharge à 619. Les données actuelles conservent notamment le pot d'huile d'Odile,
au cellier, trois charges. Ce rapport atteste un échange livré ; il n'atteste pas une négociation
de délai ni un retard. Son autre épreuve joueur est l'achat à Odile pour la lanterne de l'étable.

**Aujourd'hui.** Une part peut être payée puis réellement livrée ; recevoir la part ne recharge
pas la lampe. Le paiement, l'engagement, le remboursement éventuel et les gestes de recharge
sont distincts. Le délai générique d'abandon de l'engagement est de 240 minutes ; une date
estimée par un devis peut servir au suivi, sans devenir une date choisie par les parties.

**Ce qui manque.** Exprimer et juger « cette livraison avant dix minutes », conserver cet accord
et le comparer au résultat réellement daté. Ni une promesse de livraison ni une réussite du devis
ne signifient « lanterne allumée avant dix minutes ».

**Choix joueur.** Payer maintenant une part livrée dans dix minutes, accepter un délai plus long,
aller chercher lui-même une ressource accessible ou choisir un autre fournisseur. La recharge
reste à sa charge, sauf prestation supplémentaire explicitement convenue. Cette séparation
offre un arbitrage de jeu sans inventer une nouvelle tâche ni un besoin privé chez Odile.

### 1.3 Crue : emprunter la torche jusqu'à une date convenue

**Source directement relue :** même capture que 1.1. À 540, Ilse obtient la torche de Brune
et l'allume ; à 543, elle la rend. À 590, une nouvelle demande reçoit une contre-offre
`necessaire`. Ces événements attestent un prêt utile et un besoin concurrent, pas un retard.

**Aujourd'hui.** `biens.preter` autorise l'usage et crée une obligation de retour ; la remise
au propriétaire clôt le prêt. La règle est de rendre quand on n'en a plus besoin. Le cycle
d'engagement conserve aussi son abandon générique ; aucun accord général ne fixe ici la date
du retour. Une cession par `proposition` n'est pas ce prêt.

**Ce qui manque.** Une date de restitution commune au prêt, à la permission d'usage, au jugement
du prêteur et à la réclamation. « Tu peux la garder jusqu'à… » n'est ni « allume-la avant… »
ni une prolongation de son combustible. Une torche consumée ne revient pas par expiration.

**Choix joueur.** Demander une fenêtre d'usage pour explorer, proposer une restitution plus tôt,
acheter une source ou renoncer. C'est une extension ultérieure de l'échéance, avec une épreuve
sur un autre bien durable ; le premier périmètre de 1.2 ne doit pas la simuler par une cession.

### 1.4 Auberge : « tes gages demain » demande d'abord une vraie créance locale

**Source de scénario, sans nuit attestant ce règlement :**
[`scenario_auberge.json`](../donjon/scenario_auberge.json), `dialogues_pnj.joss` et
`objets.joss.profil`. Le portrait dit qu'Odile doit trois mois de gages à Joss ; la situation
de Joss porte `projet: 30`, sans créance locale chiffrée et sourcée envers Odile.
Le [rapport 184](taches/rapport-codex-184-naissance-agendas.md) distingue précisément obtenir
des pièces, régler une dette extérieure et établir une créance locale subjective.

**Aujourd'hui.** Un projet d'argent, les fonds d'Odile, les comptes issus de transactions et
le texte sur les gages sont des données différentes. Le portrait ne suffit pas à créer un dû
de trente pièces, et l'axe relationnel `dette` n'est pas un solde monétaire.

**Ce qui manque.** Admettre une créance locale avec parties, montant, preuve et connaissance,
puis un paiement différé, son exigibilité et sa renégociation. Il manque aussi une référence
temporelle publique pour interpréter sans ambiguïté « demain » ; l'horloge mécanique seule
compte des minutes et des dixièmes, pas une date civile négociable générale.

**Choix joueur.** Comme médiateur, demander ce qui est réellement dû, proposer une avance ou
une date de règlement. Le moteur doit distinguer un paiement volontaire d'une dette reconnue.
Cette scène motive une suite ; elle ne justifie ni un crédit créé par Luna, ni un prélèvement
automatique chez Odile à l'heure dite. Elle ne fait pas partie du premier périmètre proposé.

## 2. Briques disponibles et lacunes communes

Les chemins suivants sont dans `donjon/`. Leur présence a été vérifiée sur cette branche ;
les garanties de leurs rapports restent limitées aux épreuves qui y figurent.

| Brique | Réemploi pour l'échéance | Réemploi pour la menace ; manque réel |
|---|---|---|
| `propositions.schema_terme`, `erreur_terme`, `echanges.proposer`, `evaluer_proposition` | Termes objet/part/tâche/pièces/rien, jugement P/G/L, devis subjectifs, transaction sur copie. Les pièces sont un paiement présent ; pas de champ général de date négociée. | La demande et sa contrepartie peuvent être réutilisées, mais une sanction n'est pas un gain offert. Ne pas récompenser l'auditeur pour « éviter le coup » dans le prix ordinaire sans contrat propre. |
| `agendas.prendre`, `en_cours`, `tenir`, `echoir`, `observer_promesses` | Engagements, réalisation joueur, sortie, mémoire, remboursement. Leur identité actuelle condition/pour/minute et les liens d'origine demandent une référence stable pour les versions d'un accord. | Peut porter une obligation consentie sous contrainte ; la peur n'est actuellement pas une origine générale de consentement ni une raison d'abandon discret. |
| `agendas.aide_echue`, `suivis_delegations`, `echanges._echeance_devis` | Suivi sur croyances et durée physique, résultat contrôlé après retard. L'échéance estimée d'A5 n'est pas un engagement contractuel. `renouveler` ne doit pas pouvoir déplacer une limite négociée tout seul. | Contrôle local et comptes rendus réutilisables ; aucune notification omnisciente du refus, de la fuite ou de la réalisation de la menace. |
| Protection : `occasion_protection`, condition `{objet, proteger, echeance}` | Une fin datée existe déjà pour ce service durable ; elle ne généralise ni le maintien d'un état ni la livraison avant une date. Préserver cette sémantique. | Utilité d'un protecteur, danger et force estimés ; le secours possible ne signifie pas que le protecteur a entendu la menace. |
| Relations : `confiance`, `peur`, `rancune`, `dette`, `ascendant` ; `EPREUVES` | Fiabilité d'une promesse, parole tenue/abandonnée, dette sociale, preuves dédupliquées. Ne pas appliquer deux fois l'épreuve lors de l'expiration puis de son annonce. | Peur/rancune après coups et violences vues, liens orientés et estompement. Il manque l'épreuve d'une menace entendue, son poids et son démenti ; aucun bonus de peur arbitraire à toute demande. |
| Jugement : `echanges.accueil`, `_juger_tache`, `paroles.jet_persuasion`, `relations.autorite_mandat` | Garder droits, faisabilité, prix, accueil et jet existants. Ajouter la contrainte de temps dans le devis et le verdict communs, sans second jugement caché. | A5 distingue adhésion/dette/autorité, pas obéissance contrainte. Ses refus d'accueil restent en vigueur. Faire céder malgré méfiance ou rancune est une décision nouvelle, pas un raccord gratuit. |
| Force 4b–4e : `combat`, `defense`, `tenir`, corps et portes | Priorités de survie et interruptions conservent leurs garanties ; un délai n'impose pas de traverser un péril ou de finir un geste interrompu. | Coups/assommement, fuite/protection/reddition, prises/liens/enfermement, tuer une cible sans défense et issues différées. Disponibles comme capacités, pas comme motivations autonomes générales. `force.force_crue` relaie `combat.force_crue` sur armes/blessures connues ; aucune lecture de la FOR privée adverse. |
| Avis 3f : `social`/`eau`, parole `avis` | Sources, conviction, prévision distincte des faits ; utile si un lieu est cru bientôt dangereux, sans en faire une clause « avant la crue » calculable par défaut. | L'avis `attribut: menace` concerne l'eau : ce n'est pas une menace sociale. Réputation cause→réaction d'A7 et inférence générale des intentions restent à construire. |
| Paroles et rendu : `paroles`, `emissions`, `comptes_parles`, `comptes_narratifs` | Auditeurs réels, mots entendus, comptes et offres rendus par le moteur. Étendre aux dates et aux versions ; une émission ne vaut pas accord du joueur. | Enregistrer la condition et la sanction annoncées, distinctes du vrai et du coup ; aucune menace par le canal d'ambiance. |
| U-P/U-C : `comprehension`, `consentement`, `transactions`, `gestes_publics` | Aperçu exact du libre, effets lourds avant confirmation, revalidation ; le clic conserve l'acte choisi. Les clauses nouvelles doivent apparaître dans le récapitulatif moteur. | Même contrat pour une menace à effets sociaux ; elle ne peut être classée comme un simple propos léger. 4f et ses limites de fidélité restent applicables aux gestes de force ultérieurs. |

Lecture de cadrage : [agendas, A6–A8 et décisions](plan-agendas.md#9-étapes),
[propositions et avis 3e/3f](plan-relations.md#7-influencer-par-la-parole),
[force 4b–4f](plan-force.md#découpage),
[valeur du LLM, §§ 4–8](conception-valeur-llm.md#4-ce-que-luna-ajoute-et-quand-lattendre),
[rapport 245](taches/rapport-codex-245-conception-a5.md) et
[jugement A5, rapport 256](taches/rapport-codex-256-jugement-mandat.md).
Le contrat plus récent d'AGENTS prévaut sur les passages anciens confiant la formulation
des résultats mécaniques à Luna. A6 est partiel ; A7/A8 ne sont pas des dépendances acquises.

## 3. Comparaison et choix recommandé

| Critère | Échéance négociée | Menace |
|---|---|---|
| Choix joueur nouveau | Acheter du temps, refuser une attente, choisir un autre moyen ; dates et obligations contrôlables sur la fiche. | Faire céder sans coup, bluffer, protéger ou fuir ; changement plus profond du rapport social. |
| Richesse PNJ attendue | Offres qui diffèrent par délai, engagements réellement tenus ou manqués, contrôle du retard ; bénéfice limité si aucun PNJ ne propose/judge ces dates. | Alternatives à la violence, secours, rancune et réputation ; risques d'intimidation répétée, d'obéissance automatique et de représailles en chaîne. |
| Plus petit manque cohérent | Accord temporel explicite → jugement → réalisation datée → observation → sauvegarde/rendu. | Parole conditionnelle → crédibilité subjective → comparaison des recours → éventuelle obligation contrainte → suites et répétitions. |
| Limites à respecter | Pas de paiement différé, prêt daté, maintien continu ou sanction implicite dans la première livraison. | La force crue seule ne juge ni la volonté d'agir ni une dénonciation ; A5 n'autorise pas la peur à franchir ses refus. |

L'échéance permet de prouver un contrat commun sur l'huile, un repas, une livraison d'objet
et une tâche de feu ou de verrou, sans coder ces exemples. Son intérêt doit être constaté
en choix et conséquences, pas en longueur de dialogue. Le gain autonome est à éprouver dans
un lot séparé ; le simple ajout d'un champ ne constitue pas une richesse PNJ démontrée.

**Invariant proposé :** une limite temporelle n'engage que les parties qui l'ont acceptée,
sur une obligation et une version identifiables. Demande, jugement, éventuelle contre-offre,
exécution, constat, comptes, rendu et recharge se réfèrent à cette même version. L'expiration
du temps n'établit ni une réalisation, ni sa connaissance à distance, ni une sanction exécutée.

### Contrat minimal du premier périmètre

- **Sémantique.** « Accomplir au plus tard à T », pour les prestations ponctuelles déjà
  admissibles et les livraisons de parts. Aucun ajout de condition libre. « Tenir allumé
  jusqu'à T », un mandat social `amener`, une restitution de prêt et « payer à T » ne sont
  pas convertis en tâche ponctuelle. Leurs voies actuelles restent disponibles sans cette
  nouvelle clause tant qu'un portage propre ne fournit pas leur garantie.
- **Temps.** Une saisie relative est résolue une fois en instant absolu de jeu, dans l'unité
  exacte de `temps.instant` (dixièmes de seconde). Forme indicative : `delai: {limite: T}`
  sur le terme de prestation ; l'engagement en garde la même valeur, son identité et sa version.
  Le nom définitif du champ appartient au lot de socle. Afficher une durée restante et un
  repère absolu de jeu lisible. « Demain/minuit » demande un repère public ou une précision ;
  Luna ne fabrique pas un calendrier. Le moment de confirmation ne recalcule pas « dans dix minutes ».
- **Trois dates distinctes.** La limite acceptée, l'estimation de réalisation et l'ancien
  maximum d'abandon sont des concepts distincts. Pour une nouvelle obligation ponctuelle
  datée, la limite acceptée remplace le maximum générique ; elle ne s'y ajoute pas comme un
  second couperet. Les anciennes obligations conservent leur règle, sans date rétroactive
  inventée ; les protections datées gardent leur fin actuelle et les mandats leur suivi.
- **Jugement.** Même devis subjectif et même prix que le marché commun, avec une estimation
  de durée physique distincte du coût moral/pondéré. Une impossibilité crue de respecter T
  refuse cet accord. Une durée indéterminée dit « je ne peux pas m'engager sur ce délai » ;
  ce n'est pas la preuve que la tâche est impossible. Pas de garantie de succès, pas de
  jet additionnel qui ferait céder une impossibilité matérielle. Le délai ne dépasse jamais
  les priorités vitales. Les refus et devis mémorisés incluent les termes temporels pertinents.
- **Accord.** Le brouillon ne parle, ne prélève et n'engage pas. L'offre émise est une parole
  réelle. Pour une offre du joueur, la validation du joueur puis le verdict du PNJ peuvent
  conclure le marché atomique existant. Une offre PNJ attend un accord explicite de Corvus,
  sans paiement sur simple affichage. Une contre-offre est un autre ensemble de termes à accepter.
  Revalider les moyens et le temps restant à l'accord ; une limite passée est refusée,
  une offre devenue irréalisable n'est pas exécutée selon son ancien aperçu.
- **Réalisation et connaissance.** Une preuve de réalisation porte son instant : fait à T
  inclus = à temps ; après T = retard. À instant égal, traiter les issues de gestes avant
  l'expiration. Une observation tardive peut apprendre une réalisation antérieure attestée ;
  elle n'antidate pas un état seulement trouvé vrai. Séparer « délai dépassé sans nouvelles »
  de « manquement constaté ». Les règles de perception, de parole et de confiance déterminent
  quand le bénéficiaire apprend l'issue ; aucune lecture de l'esprit distant du prestataire.
- **Sortie.** Les remboursements et dettes effectives réemploient les comptes existants,
  une seule fois ; manquer la date ne crée ni amende ni violence. Une livraison payée close
  ne peut être prélevée une seconde fois par une vieille étape conservée. Une remise volontaire
  ultérieure est un nouvel acte réel ; elle ne change pas le verdict historique du contrat.
  Si une réaction relationnelle est appliquée, elle suit une preuve reçue et non un simple silence.
- **Renégociation.** Une estimation révisée ne modifie pas T. Modifier l'accord accepté exigera
  une offre de révision bilatérale ; le premier périmètre permet de modifier les termes avant
  accord, pas de prolonger un engagement conclu. Ne pas réutiliser la relance sans jet d'A5
  pour transformer une limite contractuelle.
- **MJ et rendu.** Luna compile/suggère uniquement les termes admis. Le moteur formule offre,
  accord/refus, montant, date, résultat et compte ; il sauvegarde leurs conséquences et mots
  entendus avant affichage. Toute clause non portée reçoit un refus précis avec `attendu`,
  jamais un `propos` présenté comme contrat réussi. U-P expose toutes les parties, la tâche,
  la date et le paiement présent ; U-C précède l'acte libre à engagement. Annuler est sans effet.
  Les revues de fidélité du libre à effets restent durant le portage ; ni modèle ni comparaison
  de modèles ne changent. La voie directe soumet exactement les paramètres choisis.

## 4. Si la menace est choisie ensuite

**Invariant propre :** l'événement certain est « cette parole a été émise et entendue ».
La sanction, son déclencheur et la demande sont des propositions typées ; leur vérité,
leur crédibilité et leur réalisation sont séparées. Une menace n'est ni un avis d'eau ni
un ordre doté d'une autorité nouvelle.
L'audience vient de l'ouïe commune ; seuls ceux qui comprennent les mots reçoivent ce contenu.
Les références affichées restent celles que Corvus connaît, y compris pour une voix inconnue.

Le jugement de l'auditeur compare le coût cru de céder au risque cru de refuser et aux
autres recours admissibles : fuite, secours, protection, résistance. La crédibilité vient
des moyens perçus, de la force crue, des témoins/protecteurs crus et des précédents connus
de l'auditeur. Un témoin ne donne pas mécaniquement raison à celui qui menace. La volonté,
le plan, les armes cachées et les connaissances privées du menaçant ne sont jamais lus
pour juger cette crédibilité. Le moteur peut peser la faute lorsque l'auteur choisit son
propre acte ; ce calcul privé ne devient pas une information offerte à sa cible ou à Luna.

Le bluff reste possible. Un refus ne déclenche pas automatiquement le coup promis : le
menaçant, joueur ou PNJ, peut renoncer ou choisir un autre geste ; un PNJ réévalue sur ses
propres croyances et valeurs. Une menace entendue peut laisser rancune ou peur sans que
la cible obéisse ; coefficients et démenti de la crédibilité devront être décidés et mesurés.
L'annonce répétée, sa diffusion et son éventuelle exécution partagent une identité de cause,
pour éviter de cumuler peur, jets ou obligations au simple défilement des tours.

La première réalisation devrait séparer : **M1 parole conditionnelle persistante sans
coercition ; M2 estimation subjective de la sanction ; M3 choix contraint et motifs ; M4
obligation/sortie sous contrainte ; M5 sélection autonome et limites de répétition ; M6 accès
direct puis libre** (deux lots si nécessaire). Fichiers probables : `paroles.py`, `social.py`,
`emissions.py`, puis `combat.py`/`defense.py`/`relations.py`, `echanges.py`/`agendas.py`, enfin
`pnj_propositions.py`/`deliberation.py` et U-P/U-C. Chaque lot aurait sa propre chaîne de preuve.

L'épreuve initiale serait les planches de 1.1, puis un autre bien disputé à la mine ; contre-épreuves :
cible mieux protégée, agresseur absent ou désarmé sans que la cible le sache, voix inconnue,
bluff, refus puis renoncement. Les sanctions de dénonciation ou d'enfermement ne s'ajoutent
qu'une fois leur crédibilité calculable ; elles ne sont pas des variantes de texte d'un coup.
L'obéissance malgré méfiance/rancune demeure un arbitrage explicite d'A7, distinct de l'autorité
bornée déjà décidée au lot 245. Cette piste n'est pas ouverte en parallèle de l'échéance.

## 5. Lots proposés, chacun de 30 à 45 minutes

Après clôture des raccords A5 concernés et synchronisation sur l'intégration disponible.
Ce tableau prépare des briefs ; il n'autorise pas leur implémentation dans le lot 347.
Les fichiers sont des prévisions à confirmer sur la base de chaque lot. Si le budget ne suffit
pas, scinder la famille suivante ; ne pas livrer une clause accessible dont le cycle est incomplet.

**Preuve commune P pour les futurs lots :** scénario 1.2 et autre prestation ponctuelle au
Relais ou à la mine ; chaîne entrée → jugement → effet réel → sauvegarde/recharge → monde,
fiche, comptes et paroles réellement visibles. Vérifier refus et annulation aussi. Même laps
continu/découpé, recharge autour de la limite ; aucune assertion limitée au retour d'une fonction.
Tests ciblés et fichiers voisins seulement. Le socle reste interne jusqu'au raccord complet.

| Lot et invariant unique | Fichiers prévus, sans extension aux autres mécaniques | Épreuve particulière en plus de P ; mesure |
|---|---|---|
| **E1. Une obligation conserve une référence temporelle canonique.** | `agendas.py`, validation d'état dans `esprits.py`, tests socle/engagements ; identité/version et lecture du délai facultatif. Pas de schéma joueur nouveau. | Ancienne sauvegarde et deux obligations distinctes à même minute ; pas de date inventée, protection et mandat inchangés. Empreintes neutres. |
| **E2. Le verdict temporel dépend d'une réalisation datée unique.** | `agendas.py`, points de réalisation dans `echanges.py` et `biens.py`, ordonnanceur `pnj.py`/`temps.py` seulement si nécessaire ; tests preuve/engagements/comptes. | Livraison et tâche, T−1/T/T+1 dixième, constat tardif, remboursement unique et arrêt d'une étape périmée ; mêmes mots/monde après recharge. Banc rapide. |
| **E3. Le jugement du délai utilise les moyens crus du contractant.** | `echanges.py`, `planification.duree_devis`, devis/entrées de `planification.py` et refus de `deliberation.py` concernés ; tests propositions/refus/devis. | Huile à livrer et feu à entretenir ponctuellement : délai crédible/impossible/indéterminé ; changement caché des moyens adverses sans effet sur l'estimation, changement connu la périme. Durée distincte du coût ; banc rapide. |
| **E4. L'accord initial engage exactement les termes datés acceptés.** | `propositions.py`, `echanges.py`, `agendas.py`, `comptes_parles.py`/`comptes_narratifs.py`, `emissions.py` ; tests marchés et comptes. | Termes `part` et `tache` datés, pièces payées maintenant ; refus n'engage pas, double soumission ne repaie pas, aucun champ de paiement futur accepté. Rendu moteur complet et public ; banc rapide. |
| **E5. Le choix direct conserve l'accord affiché jusqu'à la validation.** | `gestes_publics.py`, `comprehension.py`, consommateurs console/web concernés, `consentement.py` si raccord nécessaire ; tests parité interfaces. | Proposer date/prix, corriger, annuler, offre périmée ; huile et autre tâche, aucune interprétation du clic. Zéro appel modèle ; nombre de choix jusqu'à effet. |
| **E6. Le libre conserve chaque clause temporelle de l'accord.** | Schéma de `paroles.py`, compilateur/consignes communs en vigueur, `comprehension.py`, `consentement.py`, `transactions.py` ; tests MJ et fils ciblés. | « Part livrée dans dix minutes » puis tâche différente ; refus de « payer demain », « tenir jusqu'à » et clause alternative non portée, sans exécution partielle. Une passe Luna ciblée sur copies, pas de campagne générale ; banc rapide si effets moteur changés. |

**Noyau jouable après E1–E6 :** négocier les termes d'un nouvel accord ponctuel depuis
le direct ou le libre, avec date jugée et cycle complet. Cette livraison ne promet ni
contre-offres PNJ spontanées ni modification d'un contrat déjà conclu. Les trois suites
suivantes restent successives et soumises à un brief, sur le même invariant temporel :

| Suite | Invariant, fichiers et preuve ciblée |
|---|---|
| **E7. Une offre PNJ attend le consentement explicite sans engager Corvus.** | `propositions.py`, `agendas.py`, `paroles.py`, `emissions.py`, `comptes_parles.py`, interfaces d'accord ; offre durable avec auteur/destinataire/termes/révision/validité, revalidation à l'acceptation. Deux offres datées, refus/expiration/recharge, aucun paiement au stade de l'offre. Ne pas supposer que le seul paramètre `accord_joueur` fournit déjà ce cycle. |
| **E8. Une révision ne remplace l'accord qu'après nouvel accord des deux parties.** | `agendas.py`, `echanges.py`, `propositions.py`, comptes et interfaces d'E5/E6 ; référence à la version remplacée, sans nouvelle avance implicite. Date repoussée/refusée, proposition périmée, limite atteinte pendant la discussion ; pas de remise à zéro de la dette ni des preuves. Une passe Luna ciblée si libre porté dans ce lot, sinon lot séparé. |
| **E9. Un PNJ ne propose un délai que pour un recours utile qu'il croit réalisable.** | `pnj_propositions.py`, `echanges.py`, `deliberation.py`, entrées de recherche touchées ; réemploi d'E7 et des devis. Une alternative déterministe sur sollicitation/refus pertinent, pas de balayage continu de dates ni de besoins secrets. Auberge puis mine, refus retenus et absence de nouvelle proposition sans changement pertinent. Banc rapide ; offres/accords utiles et boucles comptés. |

Le prêt daté (1.3), le maintien continu et le paiement différé (1.4) feront chacun l'objet
d'une nouvelle conception/autorisation de famille. Le premier exige la cohérence permission,
restitution et réclamation ; le second une preuve de continuité ; le troisième un registre
de créances locales et un règlement volontaire réel. Aucun ne sera ajouté au détour d'E6 ou E9.

### Mesures et critères de livraison des futurs lots

Pour le socle censé neutre : empreintes **2 h, quatre graines**, scénarios réellement touchés
et Relais, références par commit en cache. Pour un changement de comportement : banc rapide
**4 h, quatre graines** (1985/7/42/2024), mêmes scénarios ; auberge/Relais/mine au minimum
quand le cycle commun change, crue/hameau si leurs engagements ou priorités sont concernés.
Pas de suite complète ni de nuit longue dans ces lots. Une passe Luna seulement pour le chemin
MJ changé ; Luna reste `gpt-6-luna`, forfait ChatGPT, copies de parties et coffre principal.

Critères déterministes : zéro clause omise, double paiement, double épreuve sociale, réalisation
antidatée, fuite d'information ou changement d'issue après recharge/découpage dans les cas P.
Un échec interdit de qualifier le contrat de général. Conserver les motifs de refus et les
alertes préexistantes, expliquer chaque nouvelle boucle/usurpation avant livraison.

Richesse : distinguer offres émises, délais acceptés/refusés, réalisations à temps/en retard,
contrôles sans nouvelles, remboursements et choix d'un autre recours ; conserver S/F/D et les
suspects des outils existants. Ne pas compter une reformulation ou un `propos` comme accord.
Temps : entrée→aperçu puis confirmation→effet, appels bloquants, coût CPU/nœuds sous charge
comparable ; aucun temps de cache comparé à une exécution actuelle. Si E9 ne produit que des
répétitions ou aucune décision nouvelle dans les scènes ciblées, ne pas annoncer de gain autonome.
Le lourd reste groupé à l'intégration, selon AGENTS. **Aucune de ces mesures futures n'a été
exécutée dans le présent lot documentaire.**

## 6. Arbitrages demandés à l'utilisateur

Les décisions ci-dessous sont des propositions ; elles ne remplacent pas les décisions acquises
sur A5, les trois agendas actifs, les priorités vitales, U-P/U-C et la transition des audits.

1. **Échéance ou menace d'abord ?** Recommandation : échéance, cas 1.2, E1–E6 puis évaluation
   avant E7–E9. La menace viendrait ensuite comme mécanique propre, sans ouvrir A7 en parallèle.
2. **Quelle première portée ?** Recommandation : accomplissement ponctuel/livraison avant une
   limite, paiement présent. Garder prêt daté, maintien continu et crédit hors de ce premier
   périmètre, avec refus explicite de leurs clauses. Cela livre une capacité complète et bornée,
   sans annoncer une négociation temporelle universelle.
3. **Que signifie dépasser la limite ?** Recommandation : clôture de cette prestation datée et
   traitement comptable existant, sans sanction nouvelle ; connaissance et réaction relationnelle
   seulement sur preuve reçue. Pas de délai de grâce caché. La limite acceptée prime le maximum
   générique pour les nouveaux accords datés ; les anciens conservent leur règle.
4. **Une durée incertaine peut-elle être promise ?** Recommandation initiale : ne pas accepter
   une garantie datée quand le devis ne permet pas de se prononcer ; exposer cette incertitude
   et laisser un accord ordinaire sans limite nouvelle. Aucun abandon silencieux de la clause.
   Le bluff sur la faisabilité d'une promesse demanderait un lot de tromperie distinct.
5. **Renégociation et autonomie PNJ dès le noyau ?** Recommandation : après E6, E7 puis E8/E9,
   chacun avec sa preuve ; une date acceptée ne bouge jamais par simple relance. Commencer les
   suggestions par une alternative à la demande, conformément à K0/K1/K2 ; aucun appel Luna
   pour calculer l'offre déterministe ni pour choisir l'accord du PNJ.
6. **Dates de jeu ou calendrier civil dès maintenant ?** Recommandation : durées relatives
   résolues et repère absolu de jeu montrés ensemble ; demander une précision pour « demain »
   sans repère établi. Reporter le calendrier et les créances locales au chantier de 1.4.

## 7. Portée de la conclusion

Les quatre scènes établissent des enjeux existants et les lacunes de contrat correspondantes.
Elles ne démontrent pas qu'un délai produira naturellement plus de richesse dans les nuits
actuelles, ni qu'une menace évitera un coup. Aucun coefficient nouveau n'est recommandé sans
épreuve ; aucune fidélité sémantique universelle ou absence générale de boucle n'est garantie.
Le choix et les arbitrages de la section 6 restent à confirmer avant les lots d'implémentation.
