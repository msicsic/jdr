# Contrat entre le MJ et le monde

Ce document décrit le contrat appliqué entre Luna (le MJ) et le moteur, et ce qui reste à
construire. Il découle de la section « Contrat du MJ » d'[AGENTS.md](../AGENTS.md).

## Trois niveaux de vérité

| Niveau | Contenu | Autorité | Contrôle avant affichage |
|---|---|---|---|
| Mécanique | entités identifiées, positions, sorties et passages, portes et attaches, possession, ressources, lumière, présence des PNJ, missions, résultats d'action, indices | moteur | doit découler des faits fournis ; une invention est refusée et passe par un fait typé |
| Interactif | objet ou détail que le joueur peut cibler | moteur, après proposition typée | validation des faits typés ci-dessous |
| Ambiance | aspect, odeur, son de fond, texture, impression | Luna | libre, enregistrée avec son lieu, ne crée aucune entité mécanique |

## Contrôle de la prose

Chaque réponse libre de Luna (dialogue, avis de clarification, explication d'un refus)
est découpée en segments et relue par un auditeur, qui classe chaque segment :

| Verdict | Traitement |
|---|---|
| `neutre` (salutation, conseil, question) | affiché tel quel |
| `hypothese` (possibilité présentée comme incertaine) | affiché tel quel |
| `ambiance` (description sensorielle) | affiché tel quel ; enregistré dans `ambiances[lieu]` avec les éléments évoqués |
| `parole` (propos d'un PNJ présent) | locuteur présent et citation exacte exigés ; enregistrée avec lieu, instant et auditeurs ; son contenu n'est pas une vérité |
| `mecanique` | doit citer au moins une clé de fait fournie (`objet:<id>`, `perception`, `salle`…) |
| `invention_protegee`, `contradictoire` | révision demandée à Luna ; jamais affiché |

Le texte accepté est affiché **tel que Luna l'a écrit**. Les ambiances du lieu courant
reviennent dans le contexte suivant (`ambiance_etablie`), ce qui permet à Luna de rester
cohérente et à l'auditeur de refuser une ambiance qui les contredit.

**Garde-fou déterministe.** Les noms et alias de toutes les entités du monde, y compris
cachées, et les noms des salles forment un lexique dérivé de l'état
([donjon/lexique.py](../donjon/lexique.py)). Un terme du lexique présent dans le texte mais
absent de tout ce que Luna a reçu (faits, conversation récente, message du joueur) entraîne
une révision, quel que soit le verdict de l'auditeur. Le même contrôle s'applique aux
textes des ajouts persistants (détail, objet, inscription, parole, portrait, savoir), le
nom de l'élément créé faisant partie de l'ajout. Il est refait au moment de l'enregistrement. Ce que croient les
personnages présents (`esprits_interlocuteurs`) n'est pas un fondement pour la narration : un
nom connu seulement par leurs croyances n'est admis que dans une réplique, entre guillemets.
Ce qu'un personnage croit ne se dit que par sa bouche.

Une réponse refusée est révisée au plus deux fois ; aucun texte refusé n'est affiché. Après
trois échecs, le jeu affiche une phrase sûre du moteur. La réponse acceptée, ses paroles et
ses ambiances sont enregistrées et sauvegardées avant l'affichage.

**Ce que le MJ reçoit d'un refus d'audit** (branche `audits-attendu`). Un refus d'audit suit le
contrat des refus du moteur (`donjon/refus.py`) : un `motif`, la règle, et un `attendu`, qui dit
où (`partie`, `segment` : l'indice du segment tel que l'auditeur l'a reçu, ou le champ d'un
ajout comme `proposition.ajouts[0].texte`), ce qui a été reçu (la phrase, le nom ou la citation
en cause, tels qu'écrits) et ce qui serait accepté, en identifiants ou citations exactes ; une
cause par refus (un mot d'auteur, un nom sans fondement, une parole racontée, une citation
nouvelle : chacun le sien). Pour un verdict d'auditeur (narratif, portée, capacités, contre-revue
d'action), `attendu` donne sa catégorie et son motif tels quels (« selon l'auditeur (verdict
invention_protegee) : « … » »), sans prétendre à plus de certitude que ce jugement. Un rapport
illisible (`refus.RapportIllisible`) ne reproche rien au texte : son `attendu` le dit. Chaque
relance reçoit tous les refus du tour dans `controle_narratif`, et la contre-revue d'action passe
par `retour_moteur` comme un refus du moteur. Ni le motif ni `attendu` ne s'affichent : un texte
refusé n'est jamais montré, et le repli ne cite que le moteur ou des phrases admises.

| Voie | Refus (une cause chacun) | `attendu` cite |
|---|---|---|
| texte vide | texte vide | la partie |
| voix d'auteur (`voix_auteur`) | un mot (« Corvus », « les faits »…) | segment, mot |
| nom sans fondement (`mentions`, `mentions_proposees`) | un nom | segment ou champ de l'ajout, nom tel qu'écrit ; jamais l'identifiant de l'entité cachée |
| parole sans moteur (`paroles_sans_moteur`) | une parole racontée de Corvus ; une citation nouvelle | segment, mots ou citation ; `parole_prevue.personnage` |
| voix inconnue, noms connus (`voix_inconnues`) | le récit nomme une voix inconnue ; une réplique, de tout locuteur, nomme qui il ne connaît pas (`voix.connait_nom` : Corvus seulement s'il a dit son nom ou qu'on le lui a dit) | segment, nom, `interlocuteurs.<voix>.nom` |
| verdicts (`controler`) | mécanique sans source, locuteur absent ou non destinataire, engagement sans appui, parole mal citée, invention, contradiction | segment, phrase, verdict et motif de l'auditeur ; clés `objet:<id>` qui la nommeraient, présents, destinataires, engagements prévus mot pour mot |
| portée (`portee_narrative.controler`) | représentation, capacité, fixation, impact, preuve, fragment sans preuve | description et sujet, ce que l'auditeur a lu |
| capacités (`coherence_physique.controler`) | qualification incompatible | qualification, objet, champs proposés |
| contre-revue d'action (`couverture_action.verifier`) | plan non conforme | titre, action et cible du plan, motif de la revue |
| rapport illisible | — | « aucune phrase n'est en cause » |

**Ce que dit une parole de Corvus validée** (branche `parole-corrections`). `conversation_validee`
porte `issue`, la phrase du moteur sur ce qui a eu lieu (Corvus a dit ces mots, à qui, qui lui
répond, qui l'a entendu sans être interpellé ; « Aucune réponse ne te parvient » sinon), ajoutée aux
attestations, et `repondent`, ceux qui répondent : ses destinataires, et à la cantonade ceux qui l'ont
entendue et ont choisi de répondre (`paroles.repondants`). Seuls ceux de `repondent` parlent
(`narration.destinataires_parole`) ; l'auditeur sait que leur réplique est une parole permise sans
« parole prévue », et que les dire muets contredit l'issue. Les objets reçus disent ce qu'ils
mesurent : `a_portee_de_main` (toucher d'ici), `a_portee_de_voix` pour un personnage ; la salle,
`sorties_connues`, avec leurs positions relatives en mètres (n'en connaître aucune n'atteste pas qu'il n'y en a pas).

**Ce qui n'appelle pas de relance** (branche `relances-luna`). Un appel au MJ ou à l'auditeur qui ne
peut rien changer à ce que lira le joueur n'est pas fait :
- un avis (`clarifier`, `impossible`) que la boucle de décision écartera avant de le lire (un
  « impossible » au premier examen, qui reçoit le réexamen ; tout avis quand la saisie est une parole
  sans conteste) n'est pas audité (`mj.refus_assure`, comme un ajout que le moteur refusera) ;
- le nom que Corvus se donne est celui que disent ses mots : le moteur le lit lui-même et remplace un
  `nom` typé autrement (`paroles.verifier_nom`) ; seul un `nom` typé sans nom dans les mots est refusé ;
- la citation d'une parole est le texte entre « et » du segment : quand l'auditeur la recopie avec les
  mots d'attribution, la réplique qu'elle recouvre en tient lieu (`narration.citation_du_segment`) ; une
  citation qui ne recouvre aucune réplique reste refusée ;
- l'explication d'un geste refusé par le monde (trop loin, absent, ce qui manque) a un seul essai :
  refusée par le contrôle, le joueur lit les refus du monde, leurs messages tels quels (voir « Refus et
  échecs »).

- « demander à + infinitif » (« tu demandes à passer sous la poutre ») demande de pouvoir faire : ce
  n'est pas une parole de Corvus racontée (`narration.parole_racontee`) ;
- un geste fait au joueur (on lui remet un objet, on lui réclame le sien) lui est dit une fois, à la
  deuxième personne ; son ouïe ne le lui redit pas à la troisième (`ouie.retentir`, `appris`).

Ce que le contrôle déterministe exige du texte est aussi dit au MJ, une fois (`narration.REGLE_NARRATION`) :
deuxième personne, ni « je » hors des répliques, ni Corvus, joueur, moteur, MJ, scénario, faits ou
données ; une voix inconnue désignée par son nom d'interlocuteur ; une réplique qui ne nomme que qui son
locuteur connaît. L'`attendu` d'une voix d'auteur dit comment l'écrire autrement (« tu ne sais pas si… »). La
contre-revue d'action sait que chercher ou fouiller se fait par une perception sur ce qu'on fouille
(la règle même que le moteur prescrit à un arbitrage d'observation) ; l'auditeur, que dire un témoin
silencieux est attesté, que les mots de qui répond ne sont jamais fournis par les faits, et que ce que
fait sentir un objet perçu dans son état (le feu allumé qui crépite) est ambiance.

**Une perception est un geste complet** (branche `codex-perception-geste`). La table
`moteur.PERCEPTIONS` déclare les perceptions du moteur ; `Plan.perception` en donne l'opération
et la cible, sans anticiper ce qu'elle révèle. Ce dossier accompagne le plan et ses étapes
dans la contre-revue, avec les désignations publiques. `Plan.realise_geste` admet une perception
comme une information ou un effet, y compris après correction d'une proposition : l'écoute
et l'observation d'une personne peuvent ne produire leur information qu'à l'exécution.
La revue juge toujours le choix du geste et de sa cible. Après sauvegarde, `jeu.conclure`
affiche directement le résultat d'une perception produit par le moteur : ce résultat est
déjà le rendu de ce qui est perçu et ne demande pas une seconde rédaction et son audit.
La règle distincte de
`commandes.PERCEPTIONS`, qui borne l'exécution immédiate d'une question, reste inchangée.

**Vue courante et perception active** (branche `codex-absence-vue`). Le fait `perception`
porte `objets_visibles`, la liste exhaustive des objets vus maintenant (`objet:<id>` avec
`visible=true`), avec l'éclairage courant. Une absence limitée à cette vue (« tu ne vois pas
de… ici ») est mécanique, source `perception`, sans exiger une recherche. Cela ne prouve
aucune absence dans toute la salle, derrière une porte, dans un contenant fermé, hors du
champ de vision ou dans le noir. Un objet accessible avec `visible=false` ou un souvenir
ne fait pas partie de cette vue. La portée se juge sur l'affirmation, même si la demande
du joueur propose de chercher ; répondre sur la vue actuelle n'exécute pas ce geste.

Le résultat positif ou négatif d'une perception active au-delà de cette portée est une
affirmation mécanique : il doit s'appuyer sur une perception exécutée, dans `resultat_resolu`
ou les résultats enregistrés. Une proposition, la demande et l'absence de faits ne prouvent
pas ce résultat. Sans source, l'audit le refuse comme invention mécanique.
Une recherche, une fouille ou un examen actif ne se remplace pas par `etablir_faits`, même
pour décrire seulement son support ou joindre une `suite`. Avant toute transaction de faits,
la contre-revue de portée reçoit la demande entière et tous les ajouts, y compris ceux sans
prose descriptive. Elle juge séparément, pour chaque ajout, s'il remplace une perception
et s'il crée un indice : un signe de passage, de présence, d'événement ou de chose cachée
reste un indice sans lien avec la quête. Chaque cause reconnue est refusée avec le champ,
l'ajout reçu et un `attendu` vers les opérations de `moteur.PERCEPTIONS` sur sa cible.
Seule la perception exécutée produit son résultat, enregistré avant affichage. La détection
de cet usage reste sémantique ; le moteur refuse tout rapport incomplet, sans enregistrer
l'ajout. Une parole de PNJ n'établit toujours que les mots prononcés.
Les aspects ordinaires et les propriétés matérielles inconnues restent proposables en réponse
à une demande descriptive. Le rendu d'un `detail` ne lui accole plus « sur » et son support :
son nom sert à le cibler, son ancrage est sauvegardé, sans construire « un sol sur le sol ».
L'ambiance reste libre lorsqu'elle ne conclut ni au résultat
d'un geste ni à l'absence d'un élément mécanique. La reconnaissance de ce sens dans une phrase
et le jugement de fidélité de la revue restent sémantiques : ce contrat ne garantit pas
l'absence de toute mauvaise classification par Luna.

**Ce qui reste probabiliste.** Le classement des segments par l'auditeur. Une affirmation
mécanique fausse formulée sans nom d'entité (« la pièce est plongée dans le noir » alors
qu'elle est éclairée), ou un objet manipulable présenté comme ambiance, dépend de son
jugement. Le banc de parties (`tools/banc_parties.py`) mesure ce résidu. Un élément
d'ambiance ciblé par le joueur doit être matérialisé ou déclaré non manipulable : voir la
matérialisation à la demande, quand elle sera en place.

**La preuve reste interne** (branche `codex-ambiance`). Le récit dit ce que tu perçois, sais ou
supposes ; il ne commente jamais ce que le moteur établit, atteste ou indique. Le garde commun de
la voix d'auteur contrôle aussi ce vocabulaire de preuve et les tours impersonnels d'absence
d'indication, indépendamment du classement de l'auditeur. Chaque refus donne au MJ le segment,
les mots reçus et un `attendu` : décrire directement l'ambiance compatible comme perçue, ou dire
la limite de perception ou de savoir d'une inconnue mécanique (« tu ne le vois pas d'ici »).
Une réplique de PNJ conserve sa liberté de parole ; son contenu ne devient pas une vérité.
Le garde est refait à l'enregistrement de la narration. La reformulation admise est sauvegardée
avec son lieu, sans création d'entité mécanique.

L'interprétation ne demande plus une ignorance ajoutée à chaque réponse d'information ; la
révision corrige la rupture désignée sans reprendre le vocabulaire de preuve du verdict.
L'auditeur juge la compatibilité de l'ambiance et non la connaissance de sa cause : une absence
de sensation peut aussi être une ambiance libre, sans conclure au résultat d'une perception active.
Le contrôle lexical n'épuise pas toutes les
paraphrases de méta-preuve : leur détection et les contradictions de sens restent sémantiques.

### Parole, références et audit après les noms (`codex-luna-noms`)

Le moteur fixe seul l'adresse : nom ou vocatif, groupe explicite, suite d'un échange.
Sans adresse ni échange à poursuivre, il choisit celui d'en face ; à égalité, le joueur
précise. Sans interlocuteur perçu à portée de voix, une parole à voix haute part à la cantonade
(`personne`). Cette règle établie est rétablie par le lot 47 b. `tous` exige une adresse de groupe. Un pronom individuel
sans antécédent (« je lui dis ») et le chuchotement se résolvent par celui d'en face ;
un chuchotement exige le contact. Des guillemets poursuivent l'échange si possible,
sinon le même défaut par le regard. Cette décision commune alimente `parole_prevue.personnage` et la
validation avant toute mutation ; Luna ne choisit plus parmi des audiences libres.
Une audience contraire à la saisie est refusée avec `attendu`, avant la contre-revue.
La contre-revue des paroles à adresse implicite juge encore le contenu et les mots ;
elle ne décide plus de l'audience. Deux contenus refusés demandent les mots du joueur,
sans lui demander à qui parler. Le secours local ne contourne pas ce refus.
Une question directe choisie comme parole conserve exactement les mots saisis.

Dans une intention non citée de forme « je <verbe> [à] <personne> … » (ou « j’<verbe> … »),
l'analyse commune conserve aussi la cible nominale du prédicat (`cible_intention`), sans liste
supplémentaire de verbes. Si le MJ en fait une parole, elle va à cette personne ; cela ne
force pas une parole pour un geste. Une mention dans le corps d'une citation ne devient
pas une adresse : seuls le vocatif et les formes de parole existantes l'y établissent.
Cette reconnaissance reste syntaxique : ni analyse grammaticale complète, ni résolution
des intentions indirectes ou à plusieurs propositions. Une cible non reconnue garde la
règle par défaut (regard, sinon cantonade) ; elle n'est pas devinée à partir de la ressource ou du scénario.

Une question au MJ sur la faisabilité d'un geste ne devient pas une parole à un PNJ voisin :
le même réexamen exige le geste à préparer. Une question explicitement dite ou adressée à un
personnage reste une parole.

Un verbe de parole sans propos, quand aucune réponse locale à un appel ne le résout, demande
au joueur ses mots avant tout appel au MJ. Une adresse nominale non résolue donne le refus du
moteur, même sans guillemets. Hors parole, `noms.verifier_saisie` résout les noms du lexique
avant toute syntaxe locale ou interprétation du MJ, y compris pour une question et `mj …`.
Un nom sans lien donne « Tu ne sais pas lequel d'entre eux est X » si des inconnus sont
perçus, sinon « Tu ne connais personne du nom de X ici ». Un nom relié mais non perçu donne
« Tu ne vois pas X d'ici » pour un geste, y compris demandé en faisabilité. Une perception
locale sur une personne reliée laisse le moteur dire sa cause (lumière, présence, regard).
Une adresse nominale passe par l'accès commun de la parole, avec ses voix distantes et son
regard ; une question adressée ne devient pas une demande d'information au MJ.
Ces refus ne révèlent ni corps ni position privée, ne font rien
apprendre et n'appellent aucun modèle, en ligne comme hors ligne. Le contrôle n'énumère pas
les gestes : les références nominales viennent de l'état, par `noms.personnage`, aussi utilisé
par la parole. Les mots cités, les appellations de voix et les désignations publiques gardent
leur sens ; héler émet un nom sans exiger la présence de son porteur. Une parole mentionnant
un tiers n'établit pas son identité. Les répliques validées et les résultats d'action gardent
leurs contrôles. Un nom absent de tout le lexique n'est pas reconnu comme nom propre par ce
contrôle ; l'interprétation et ses gardes de références restent nécessaires. Les formulations
que le parseur traite comme parole conservent ce contrat : leur contenu n'est pas analysé
comme une liste de cibles. Les formulations mixtes gardent donc une part sémantique.

**Questions sur un absent connu** (`codex-question-absent`). Le nom doit toujours être relié,
mais une demande d'information ne requiert pas sa présence : elle va au MJ avec les seuls
faits publics habituels (souvenirs, bruits, signes reçus), puis son audit et sa sauvegarde
avant affichage. Elle ne révèle ni position ni intention privée et ne produit aucun geste.
Le contrôle réemploie `commandes.est_question` (ponctuation interrogative, interrogatifs,
inversion), après l'analyse de parole, et écarte `commandes.faisabilite` ; aucun nom ni
exemple particulier ne détermine cette distinction. Ce classement syntaxique n'est pas une
compréhension générale du français : les formulations mixtes, une question sans marque
reconnue et le sens de la réponse restent soumis à l'interprétation et à l'audit sémantiques.
Le refus d'un nom non relié reste le même, questions comprises.

Tous les répondants d'une parole sont entendus avant la narration, y compris un destinataire
qui vient de s'écarter hors du champ visuel. Une voix entendue depuis une autre salle est un
interlocuteur si les mots passent encore dans les deux sens ; la salle commune n'est pas une
condition supplémentaire. Les deux voies d'enregistrement des répliques (audit et fait typé)
emploient `ouie.auditeurs_parole`, vérifient l'audition du joueur et enregistrent la salle réelle
du locuteur. Aucune voix distante ne donne un portrait ou un lien nominal supplémentaire.

La ponctuation finale d'une réplique termine son segment lorsque la phrase suivante commence ;
les locuteurs successifs ont ainsi leurs propres citations auditées. Une `presentation` que
l'auditeur fournit sans la trouver dans sa citation est écartée par le moteur : aucun nom n'est
appris, la réplique contrôlée reste inchangée et n'est pas relancée pour cette métadonnée.
Un fait typé qui prétend ajouter une
présentation absente de ses mots reste refusé par le moteur.

Une opération dont la cible n'a pas le type requis est un `RefusDeForme`. Elle ne prouve pas
qu'une ressource manque au geste réellement demandé : par exemple, `franchir` parcourt un
assemblage, pas n'importe quel obstacle. Le refus de proximité garde ses coordonnées dans
`attendu`, pour le MJ ; son message public ne contient que l'invitation à s'approcher. Une
approche d'improvisation (`effort`, `adresse`…) reste une donnée structurée de l'arbitrage et
ne devient plus le libellé narratif du geste.

## Noms et identité perçue (branche `codex-noms`)

Voir une personne fait connaître son apparence, l'entendre parler sa voix. Aucun de ces deux
faits ne donne son nom. Le nom est entendu et relié, ou déclaré comme savoir antérieur du
scénario. Une personne visible inconnue est `personne_<n>` avec une désignation visuelle
persistante ; les références de ses éléments sont opaques aussi. Le même contrat gouverne
la saisie, les propositions, les souvenirs, les rendus et la sauvegarde.

Le récit ne prononce pas un nom que le joueur n'a pas appris : contrôle déterministe même
si ce nom figure ailleurs dans une question ou un fait. Une réplique peut introduire un nom
que son locuteur connaît. Une présentation explicite, un destinataire nommé et identifié ou
la liaison de voix d'un échange établissent le lien avant affichage. Une simple mention de
tiers reste sans attribution à un corps. Le protocole de réplique MJ n'a pas de destinataire
tiers validé : cette mention seule ne présente donc personne. `noms_pour_repliques` est réservé à cette voix, sans identifier ni situer
les personnes correspondantes pour le narrateur. Une affirmation de nom reste distincte
de la vérité de l'identité revendiquée. Les citations d'une description ne sont jamais
traitées comme des paroles entendues.

Des guillemets seuls n'autorisent aucun nom privé. Seule la citation entière et unique d'une
parole auditée bénéficie de sa provenance, dans son passage précis ; les mêmes mots cités
ailleurs restent sous le garde du récit. Des mots déjà enregistrés et entendus peuvent être
restitués comme citation autonome entière, sans nouvelle attribution narrative. Ils ne peuvent
pas servir d'étiquette de corps ni de description persistante. Une sous-chaîne de parole n'a
pas cette provenance. L'enregistrement et les réponses de dernier recours refont ce contrôle.

La phase de narration après parole ou action validée reçoit le paquet privé du locuteur :
son propre `nom_du_locuteur`, séparé de `noms_pour_repliques`, les noms de tiers qu'il connaît.
Ces deux données privées sont absentes de l'interprétation mécanique, qui garde seulement les
connaissances nominales publiques du joueur ; elles ne permettent donc pas de choisir une cible.
Le locuteur peut ainsi se présenter ; ce champ ne donne ni identifiant
réel ni fait public au narrateur. Le refus déterministe du nom inconnu s'applique aussi si
la donnée privée le contient. Les champs sans sens pour un type de contenu de parole sont
refusés avant transmission, avec le champ reçu et la valeur vide attendue.

L'audit d'une réplique et le fait persistant `parole` portent une `presentation` explicite :
nom littéral dont le locuteur se présente, sinon vide. Le moteur exige ce nom dans la citation,
relie la présentation à la voix qui parle et consigne les auditeurs avant affichage. Cela
permet aussi une réponse nominale. Le classement sémantique de cette présentation reste celui
de l'audit ; il ne permet jamais d'identifier le corps d'un tiers seulement mentionné. Une
appellation de voix revendiquée ne vaut pas connaissance du vrai corps qui porte ce nom.

À la frontière de toutes les réponses MJ, les champs de référence doivent utiliser la
référence publique fournie. Un identifiant réel deviné d'une personne inconnue est refusé,
même s'il figure dans un texte privé contaminant ; seuls les mots libres et le contenu
nominal revendiqué gardent leur contrat de parole. Le décodage suit cette validation ; le
moteur interne conserve ses identifiants. La contre-revue d'action reçoit aussi les noms et
références publics. L'aperçu d'un plan passe entièrement par cette projection, opposition,
risque et étapes compris. Aucun substitut textuel ne tire l'apparence d'un corps jamais vu.

### Désignations enrichies (`codex-designations`, non fusionnée)

Le noyau d'une désignation publique et les qualificatifs qui l'entourent ont deux rôles
distincts. `noms.motif_designation` reconnaît ce noyau, avec une insertion après sa tête
nominale sans changer son complément : « la voix toute proche qui se dit Ilse » garde la
revendication « une voix qui se dit Ilse ». Le garde nominal et la projection publique ne
protègent que les mots du noyau ; les mots ajoutés restent contrôlés. « la voix d'Ilse »,
un nom privé intercalé ou une autre revendication n'acquièrent aucune identité par ce lien.

L'audit narratif et la contre-revue reçoivent `designations` : référence publique, nom
canonique, noyau ou alias reconnu, forme écrite entière et faits publics de l'entité.
Ainsi la demande « bobine de ficelle » et le plan « bobine de ficelle solide » se comparent
par leurs références et leurs faits, sans réduire la cible à deux chaînes différentes.
Plusieurs candidats restent plusieurs candidats. Aucun qualificatif n'est effacé du
texte contrôlé ou déclaré vrai par cette reconnaissance. L'aspect compatible est libre ;
une matière, une position ou une identité contradictoire reste refusée, avec `attendu`.

La compatibilité sémantique des qualificatifs reste celle des contrôles existants ; ce
reconnaisseur lexical ne prouve pas toute phrase en langue naturelle. Le complément
canonique reste contigu, sans paraphrase automatique ni résolution arbitraire d'ambiguïté.
Il ne matérialise aucun objet et n'apprend aucun nom. Les conséquences acceptées suivent
toujours l'enregistrement et la sauvegarde avant affichage, puis le contrôle à l'écriture.

## Contrôle des actions

### Portée des gestes (`codex-geste-hors-portee`, non fusionnée)

La manière d'un geste ne change pas sa portée. Les `cibles` d'`improviser` sont les
objets impliqués et doivent être à portée de main pour toutes les approches, comme
les manipulations typées. Un public ne fait pas partie de ces cibles matérielles.
Une cible désignable que Corvus verrait en se tournant est préparée dans cette
orientation, sans rotation exécutée à la question. Trop loin, le moteur renvoie
`HorsDePortee`, message « Approche-toi… » et `attendu` sur l'identifiant ; aucune
fiche de jet ni tentative n'est enregistrée. Les déplacements restent les pas
du joueur ; le rapprochement automatique des PNJ ne s'applique pas à lui.

L'opération d'un geste reste disponible quand sa cible est loin ou seulement en
souvenir. `passer_obstacle` prépare le passage dessous ou dessus ; le moteur juge
sa portée et sa géométrie. Son dossier emploie la même préparation, rotation
comprise. Les règles de l'opération ne dépendent plus de ce dossier courant.
`improviser` ne déplace jamais Corvus : la contre-revue exige une opération de
déplacement pour une demande qui change sa position. Cette fidélité sémantique
reste faillible ; le contrôle de portée des cibles, lui, est déterministe.

### Précisions du contrat (`codex-luna-restes`)

Les localisations transmises au MJ (objets, souvenirs et sorties connues) sont des repères
calculés en mètres : le plan représente un mètre par unité. Les positions brutes des sorties
restent privées, comme celles du joueur et des objets. Le récit n'utilise ni cases ni coordonnées.
Le contrôle déterministe de la voix d'auteur refuse aussi le vocabulaire du quadrillage et les
écritures de coordonnées, y compris dans les répliques et les ajouts persistants ; ce contrôle
est refait avant l'enregistrement d'une narration, d'un fait, d'un portrait ou d'un savoir. La carte technique conserve ses axes et sa
légende : cette règle concerne la fiction affichée, pas l'outil cartographique.

Depuis `codex-audience` (lots 47 et 47 b), le rapport de fidélité d'une parole porte seulement
`contenu_conforme` et `motif`. Le dossier de cette revue est limité à `replique`, `contenu`
et `sens_contenu` : aucune adresse, aucun auditeur ni conséquence mécanique à rejuger.
Les sens typés décrivent la demande ou l'affirmation, indépendamment de leur audience.
Le moteur conserve l'autorité sur l'adresse, les répondants et les conséquences calculées
sur copie ; la narration reçoit ensuite la conversation validée entière.
Une demande d'achat est une parole dont le moteur décide l'acceptation, le transfert ou
le refus ; elle n'a pas à porter une opération de transfert faite par Corvus.
Les références sont projetées en noms publics ; les mots libres restent littéraux.
Les refus d'adresse déterministe et de contenu ont chacun leur `attendu`.
La reconnaissance syntaxique de l'adresse reste bornée aux formes de `paroles.analyser` ;
la fidélité du sens des mots et le choix de parler restent en partie sémantiques.
Le sens de tous les types de contenu et des codes de ressource vient de `paroles.SENS_CONTENU`
et `RESSOURCES_DEMANDEES`, partagés par le schéma d'interprétation et la revue (`sens_contenu`).
Ainsi un besoin typé désigne la ressource recherchée ; il ne devient pas le sujet littéral de
la question. Cette donnée ne décide pas si le destinataire la possède ni s'il l'accorde.

Le contenu `proposition` d'une `parole_joueur` forme un marché indivisible :
`{type:"proposition", demande:<terme>, contrepartie:<terme>}`. Il s'adresse à un seul
destinataire et constitue l'unique élément de `contenu`. Un terme est `{type:"objet"|"part",
objet:<identifiant connu>}` ou `{type:"tache", condition:{objet, allume:true|verrouillee:true|
lieu:<salle connue>}}`. La contrepartie admet aussi `{type:"pieces", montant:<entier positif>}`
et `{type:"rien"}`. Aucun `sujet`, `attribut` ou `valeur` sur cette variante ; le schéma expose
une union avec les contenus historiques. Toute forme refusée reçoit un `attendu` portant le
chemin, la valeur reçue et la forme ou les identifiants acceptés.

Le moteur évalue P/G/L, les croyances et les moyens, puis le jet ; il inscrit les remises et
les engagements avant la réponse. Les contreparties matérielles sont immédiates, les tâches
sont différées. Un bien demandé ailleurs peut devenir une livraison engagée. Une réplique
respecte les faits calculés (acceptation, cause unique du refus, remise ou promesse), sans
transformer une promesse en réalisation. La fiche et le contexte conservent les promesses du
joueur après rechargement ; un effet réel du joueur et l'observation de la condition sont requis
pour solder la parole. Le texte libre de Luna reste soumis au contrôle narratif existant ;
le typage d'une formulation libre en proposition n'est pas garanti.

Toute qualification physique passe d'abord par la validation déterministe sur copie (ancrage,
propriété encore libre, bornes, masse quand la description la détermine), puis par la revue de
plausibilité. Celle-ci reçoit les propriétés connues, dont la description physique, le contenu
et la géométrie existants, et les `champs_a_etablir`. Une information inconnue n'est pas une
incompatibilité : le MJ peut la préciser d'après ce qu'est ordinairement cet objet, sans la
déduire du résultat souhaité. Cela vaut pour toutes les descriptions physiques, y compris le
vide et les appuis autour d'un obstacle ; aucune forme ni donnée de scénario n'est ajoutée
automatiquement. La plausibilité par rapport au nom et au texte reste sémantique. Le moteur
garde ses contrôles numériques et interdit de réécrire une forme déjà établie.

Une question explicite de faisabilité dont le geste attend une propriété physique inconnue
(`ProprieteInconnue`, dont `QualificationRequise` pour la coupe, le son et la lumière) reçoit cette
raison dès le premier refus : une fiche ne doit pas inventer ses préconditions. Une demande de
geste garde la voie de qualification puis réexamen lorsque la mécanique la demande. Les autres refus, dont un outil disponible
mais omis du plan, gardent leur voie de correction. Si Luna commence par une qualification valable, elle est enregistrée avant la fiche
et le geste est réexaminé selon le contrat existant.

`etablir_faits` peut joindre aux `ajouts` une `suite`, proposition du geste demandé. Pour une
question de faisabilité, le schéma exige cette suite si Luna choisit d'établir des faits.
Il s'agit de deux propositions dans un même appel : les ajouts passent les contrôles physiques
sur copie, puis le geste passe la préparation du moteur et sa contre-revue de fidélité sur
cette copie. Les faits acceptés sont sauvegardés avant la fiche ; la question n'exécute aucun
geste. Une propriété inconnue reçoit donc soit son manque dès la préparation, soit une
qualification et une fiche en trois appels (interprétation, physique, fidélité), sans supprimer
de contrôle ni demander une nouvelle interprétation. Cette composition vaut pour tous les
faits, pas seulement pour la forme d'un obstacle. Les propositions incorrectes peuvent encore
demander une correction ; trois appels n'est pas une borne absolue en présence d'erreurs du MJ.

L'absence d'un fait ne prouve pas son contraire. Un verdict narratif `contradictoire` doit citer
au moins une source fournie : sans elle, le rapport est redemandé à l'auditeur avant toute
demande de réécriture au MJ. L'ambiance libre compatible avec l'état est perçue et enregistrée
avec son lieu ; elle ne réclame pas de réserve qui la démente. La révision distingue l'inconnue
mécanique de cette liberté sensorielle. Une source citée à tort ou une contradiction formulée
sans élément mécanique explicite dépend encore de la lecture sémantique.

Avant l'exécution d'une action proposée par Luna, une contre-revue indépendante compare
la demande du joueur aux opérations du plan. Elle ne juge que l'état : action et cibles,
changement durable demandé mais absent, changement durable ajouté sans demande. La
manière du geste (style, position des mains, caractère d'un son) relève du récit, portée
par l'outil et la méthode. En cas de doute, le plan est accepté : le moteur garde
l'autorité sur chaque effet. Les conséquences affichées viennent du journal du moteur.

## Faits typés persistants

Luna peut proposer un groupe de faits structurés : détail visible, inscription ou parole. Le
moteur vérifie les supports et locuteurs disponibles, la perception et la forme des données.
Les descriptions de détail et les facettes de personnage passent aussi par une contre revue.
Le nom et chaque phrase sont soumis séparément. Luna découpe chaque entrée en fragments
contigus et cherche les affirmations vérifiables indépendamment du sujet proposé. Le moteur
vérifie que les fragments couvrent tout le texte. Un fragment porte sur le sujet, sur une
attestation exacte de l'état courant, sur l'ambiance autour du sujet, ou il est sans preuve ;
un fragment sans preuve entraîne une révision avant toute mutation.
L'inscription et la parole sont conservées comme textes cités ; leur contenu n'établit pas
la vérité de ce qu'elles disent. Le moteur applique ensuite le groupe sur une copie.
Les détails deviennent des cibles ; une parole est
enregistrée avec son auteur, son lieu et ses auditeurs, sans transformer son contenu en vérité.
Le texte affiché est construit à partir des faits acceptés. Si la proposition est refusée,
Luna reçoit la raison et peut la corriger. La TUI et la console sauvegardent la
transaction avant affichage.

Un fait typé ne permet pas encore de créer le support lui-même. Le contenu d'une inscription
est établi comme **texte gravé**, pas comme vérité de ce qu'il affirme.

## Ce qu'une phrase engage

- Une affirmation mécanique du MJ doit être compatible avec l'état déterministe. Une ambiance (une odeur, un aspect décoratif) est enregistrée avec son lieu avant affichage. Si le joueur la cible, elle doit recevoir une identité et des interactions générales, ou être déclarée non manipulable ; une gravure lisible porte son texte et les conditions de lecture.
- Une parole attribuée à un PNJ établit que ce PNJ a prononcé ces mots, à cet endroit et à cet instant. Le contenu peut être faux. Le moteur détermine les témoins capables de l'entendre et conserve cette parole dans leur mémoire ; elle ne devient pas automatiquement une vérité du monde.
- Une phrase du joueur établit son intention ou sa parole, pas la réussite du geste ni la vérité de ce qu'il affirme.
- Une hypothèse, une métaphore ou une possibilité annoncée par le MJ doit rester marquée comme telle. Elle ne peut être réutilisée comme observation certaine.

## Portée des ajouts

1. **Ambiance et détail local** : ajouter un fait descriptif compatible, situé et persistant, sans modifier une mission ni créer une solution.
2. **Élément interactif** : créer ou compléter une entité du monde avec identité, position, propriétés perceptibles et actions possibles. La validation du moteur précède sa première mention affirmative.
3. **Évolution du scénario** : exiger un déclencheur établi, une cause et des conséquences explicites. Un objet de remplacement ou un nouvel indice de quête ne peut pas naître d'une description destinée à combler un silence. Un obstacle provisoire, comme le manque de lumière, ne rend pas automatiquement l'objectif inaccessible.

Le Relais des crues désigne une cloche précise comme objectif. Une seconde cloche peut exister si une évolution de l'histoire le justifie et si l'état de la mission est mis à jour explicitement. Une seconde cloche affirmée dans la prose est une `invention_protegee`.

## Objets, capacités et évolutions

Le type `objet`
crée une entité physique située, dotée d'une masse, d'une matière, d'une mobilité et d'une
relation au support : `pose`, `fixe` ou `contenu`. Le support annonce les relations possibles ;
les sols portent les objets et seuls les contenants ouverts peuvent en recevoir. Le moteur
formule cette relation depuis l'état enregistré. Un objet fixé et amovible doit être détaché
avant ramassage ; une attache simple se libère à la main, tandis que les fixations du scénario
déclarent une extraction avec outil. La contre revue classe séparément les relations affirmées
par le nom et la description et refuse celles qui ne correspondent pas à la transaction. Le type
`evolution` ne contient qu'un identifiant de transition déclarée par le scénario : ses
conditions et ses effets physiques ou son nouvel objectif sont définis dans la partie,
validés par le moteur et appliqués une seule fois. Chaque condition doit porter sur un objet
actuellement visible ; le déplacement déclare son lieu de départ et l'évolution d'objectif
nomme la cible précédente. Une transition devenue périmée cesse d'être proposée. Luna ne
peut pas soumettre librement un
nouvel objectif ou téléporter un objet par une phrase descriptive.

Les objets inventés déclarent aussi une liste de capacités physiques : son avec intensité,
lumière avec niveau et combustible, ou outil avec les usages `couper`, `levier`, `allumage`
et une puissance bornée. La contre revue vérifie que le nom ou la description
annonce ces capacités et qu'aucune capacité annoncée ne manque à l'état. Le moteur borne les
valeurs, crée la source lumineuse éteinte et emploie les opérations ordinaires pour la faire
sonner ou l'allumer. Les outils improvisés passent par les mêmes contrôles de portée,
portage et usages que les outils du scénario. Le déplacement des objets, y compris lors d'une transition de scénario,
passe par la même mutation du lieu, de l'attache et de l'ancrage visuel.

La cible d'une coupe peut déclarer `tranchable` avec un seuil de puissance et une
ténacité. Le moteur compare l'outil à ce seuil, puis réduit l'intégrité à chaque geste
réussi. Le nom du matériau n'est plus une condition codée. Une coupe partielle est
annoncée comme une entaille ; l'intégrité nulle signifie que l'objet est brisé. Ce
modèle ne crée pas encore deux fragments réutilisables à partir d'un objet sectionné.

Une capacité manquante sur un objet déjà connu peut aussi passer par le même contrat
de faits persistants : `qualification` vise son identifiant et propose des capacités
bornées. Le moteur exige un objet observable à portée et refuse d'écraser une capacité
établie. Pour la coupe d'un objet existant, Luna déclare `moyen` et `coupe_possible` :
le jugement porte sur la paire cible–outil dans leur état présent et ne réécrit ni
l'intégrité ni le maximum. Il est sauvegardé avant la tentative.
Une contre revue distincte juge sa compatibilité avec la matière et la description.
Le MJ réexamine alors l'intention initiale ; le joueur n'a pas à la répéter. Cette
contre revue sémantique peut se tromper, donc ses jugements ne garantissent pas à eux
seuls la justesse physique d'une propriété nouvellement inventée.
Les objets créés avec un seuil de coupe, ainsi que ceux des scénarios qui en possèdent
un, suivent cette règle numérique déclarée. Un objet existant sans seuil reçoit un
jugement limité au moyen examiné : une scie peut donc couper après qu'une hache a été
écartée, même si sa puissance numérique est inférieure. La puissance règle encore les
dégâts ; elle ne sert pas de preuve de compatibilité entre moyens différents.

Le même type `qualification` peut consigner un jugement positif ou négatif de coupe.
Le refus conserve l'état physique de l'objet et de l'outil : il cesse de s'appliquer
si l'un change. Une aptitude positive subsiste après une entaille tant que la structure
des deux objets et leur usage restent les mêmes. Les jugements anciens restent des
souvenirs, signalés comme tels dans la description. Ils sont relus par la contre revue,
enregistrés avant affichage et repris après rechargement.
Si Luna ne formule pas correctement la réponse qui suit, le compte rendu déterministe
du fait validé reste affichable et sauvegardé ; aucune action fictive n'est créée.

Un support mural peut déclarer une case d'affichage distincte de la case de contact.
Cette case est validée comme mur voisin, héritée par les objets qui y sont fixés et conservée
dans le souvenir visuel. La portée et la visibilité continuent à partir de la face accessible.

Ces mécanismes ne donnent pas encore toutes les capacités d'un objet improvisé : d'autres
usages comme ouvrir une serrure demandent encore des propriétés et opérations validées.
Une fixation improvisée
amovible utilise pour l'instant un détachement manuel ; les fixations nécessitant un outil
demandent une propriété physique plus précise. Le classement
sémantique de la prose reste probabiliste. Les tests couvrent la chaîne
saisie → proposition → rejet ou persistance → affichage → rechargement, avec des réponses
simulées qui contredisent volontairement l'état du monde.

## Refus et échecs

**Sens partagé d'une demande de ressource** (`codex-ressource`). Le contenu `ressource`
demande une disponibilité, sans remise, achat ni promesse. Son `sujet` conserve le bien
nommé par le joueur, sans article : un nom, alias, matière ou catégorie explicite des
objets, même si Corvus ne connaît encore aucun exemplaire. L'enquête compare des suites
de mots entières dans ces données, sans synonymes déduits. Elle ne cherche que parmi
les possessions connues de l'interlocuteur, où il les croit et encore disponibles selon
ses croyances ; ce qu'il porte ou possède à portée est constaté avant sa réponse.
Une recherche sans résultat établit seulement sa réponse négative, jamais l'absence
du bien dans le monde. Les codes `faim` et `chaleur` conservent leur sens plus large de
ressources utilisables pour satisfaire un besoin général ; ils ne remplacent pas un
bien précis. `paroles.SENS_CONTENU`, le schéma et `sens_contenu` donnent ce même sens
à l'interprétation et à la contre-revue. Celle-ci peut toujours refuser un autre bien
ou un élargissement de sens ; la correction littérale est acceptée par le moteur.
Le choix sémantique du contenu et le jugement de fidélité restent probabilistes.

Un refus de forme (`refus.RefusDeForme` : un champ, une borne, la mauvaise action, « impossible »
sans réexamen) ne dit rien du monde : il revient au MJ avec son `attendu`, avec une correction à
part de la correction ordinaire (trois propositions au plus), et ne se montre jamais au joueur ; à
une question de faisabilité, le joueur ne lit tel quel que le refus d'une raison du monde.

Un refus de validation survient **avant** l'action. Seul un plan exécuté peut produire un
échec du personnage, du temps écoulé ou une conséquence physique. Après deux propositions
invalides, Luna peut expliquer les conditions attestées sans annoncer une tentative de
Corvus. Si un refus du monde a été rencontré (un `ErreurMonde` du moteur, ni refus de forme, ni
contre-revue), cette explication a un seul essai : refusée ou manquée, le joueur lit les refus du monde,
dans l'ordre, une fois chacun, dont les messages s'adressent à lui (« La lumière est trop faible pour
lire avec précision. La torche n'a plus de combustible. ») ; sinon, après trois essais, un message sûr
précise qu'aucun geste n'a été tenté.
