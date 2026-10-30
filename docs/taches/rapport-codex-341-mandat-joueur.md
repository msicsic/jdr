# Lot 341 — A5.9, le joueur mandant et mandaté

Branche `codex-mandat-joueur`, **non fusionnée**, base fournie `fff9aab`
(`origin/integration`). **Lot terminé**, moteur `113d15a`, validation `9a8c204`,
branche poussée. Dépendance 340 intégrée sans rebase par `82f5884` : conflit
documentaire seul, deux côtés conservés. `jeu.py` inchangé.

**Reprise avant fusion, demandée après livraison : validation en cours.**
`origin/integration 4379616` fusionnée sans rebase par `417e67f`, parents
`a54b3f2` et `4379616`. Conflit documentaire seul ; les sources du jeu sont
identiques avant/après, dont les sept modules partagés avec 340. Invariants
340 et 341 conservés. Reprise des 18 fichiers ciblés, dont les deux fichiers
explicitement demandés du 340 ; aucune suite complète ni nouvelle nuit.

La première reprise sur `f2e9775` donne **174/174 tests verts, 18 fichiers,
214,545 s**, dont ascendant et socle. Sa passe Luna (cinq tours, quatre MJ,
douze appels) est sans erreur technique mais **sémantiquement en échec** :

| Saisie de la reprise | Typage et issue effectivement observés |
| --- | --- |
| Amener Brune dans l'échoppe | `mandat/amener`, rejet de référence avant parole ; aucun jugement PNJ. |
| Informer Brune du brasero dans l'antichambre | `mandat/informer`, mais `operations_demandees.affirmation=true` en plus : couverture rejetée avant parole ; aucun jugement PNJ. |
| « Aubin, Brune est ici, dans le refuge du relais. » | `propos`, toutes les opérations fausses : la parole est entendue mais l'information n'est pas transmise. Défaut de typage. |
| Informer Brune du fanal dans le refuge | `mandat/informer`, parole prononcée ; jugement sauvegardé `issue=impossible`, `raison=impossible`. Aucun accord. |
| `fiche` | Commande directe, jugement précédent conservé. |

Le `fin.json ok=true` de cette reprise ne portait que sur l'exécution
technique. L'analyse ajoutée ensuite reste rouge :
`reprise-integration/validation/analyse-luna-posthoc.json`.

**Correction du contrat commun**, sans mot-clé ni exception de scénario :
les définitions partagées de l'interprétation et de la revue distinguent
l'acte immédiat de Corvus du contenu confié pour une transmission ultérieure.
Une information représentable reste une affirmation même visible ou déjà
connue. Le schéma du fait imbriqué décrit sa portée différée, plutôt que de
lui attribuer la définition d'un acte direct. Le contrôle de couverture reste
strict ; deux cas avec MJ simulé conservent croyances, refus et paroles après
recharge lorsqu'une affirmation autonome a été déclarée à tort.
La validation contrôle désormais les types attendus du script, la cohérence
de la carte d'opérations et les jugements effectivement rechargés, en plus du
code de sortie. Cette correction `b76dd31` donne **175/175 tests verts,
18 fichiers, 232,175 s**. La passe Luna type correctement les trois mandats
et l'affirmation préalable ; les cartes d'opérations sont cohérentes.
Le brasero reçoit le jugement `impossible` ; le cas du fanal reste toutefois
rejeté par la revue de fidélité, qui distingue à tort « refuge du relais »
et `antichambre`. Aucune acceptation : la réponse libre de repli n'est pas
un refus PNJ enregistré. Preuve :
`validation-portee/analyse-admission-posthoc.json`, rouge sur la quatrième
saisie, malgré le bilan de typages initial vert conservé.

**Références de revue.** Le rendu nommait seulement les champs du premier
niveau du contenu. Il parcourt désormais le registre commun des références
à toute profondeur, notamment faits et conditions, sans réécrire la prose.
Aucune exception propre au lieu, à l'objet ou au mandat. Deux témoins rouges
avant correction (`antichambre` et `chambre_cloche`) puis verts après,
avec jugement réel, mots moteur et sauvegarde/recharge. Le validateur exige
aussi que le cas réalisable atteigne le jet commun (`accepte` ou `refus`).
Nouvelle vérification détachée : vingt fichiers ciblés et une passe Luna,
fin `reprise-integration/validation-references/fin.json`. Les huit paires
initiales ne sont pas rejouées pour les seules définitions et données de
revue du joueur.

Précision saisie par saisie sur la **première passe Luna** :

| Saisie | Contenu de Luna | Décision moteur et preuve |
| --- | --- | --- |
| « Aubin, je te confie la charge d'amener Brune dans l'échoppe. » | Deux propositions `type=mandat`, `sorte=amener`, `qui=[brune]`, `lieu=l'échoppe`. | Rejet de référence inconnue avant parole. Aucun jugement PNJ et aucune charge publiée. Ce n'est pas un refus d'Aubin. |
| « Aubin, je te confie la charge d'informer Brune que le brasero est dans l'antichambre. » | `type=mandat`, `sorte=informer`, `qui=[brune]`, `fait={type:affirmation, sujet:brasero, attribut:lieu, valeur:antichambre}`. | Parole prononcée ; jugement persisté : `issue=impossible`, `raison=impossible`, avant jet. Abus aussi enregistré : `cause=honnetete`, `prix=37,142857` ; Aubin croit le brasero à l'échoppe. |
| `fiche` | Commande directe, aucun appel Luna. | Lecture de la fiche. |

Aucun échec de typage dans cette passe : ni `propos` ni autre opération à la
place du mandat. Les propositions historiques ont été rejouées sans modèle,
causes conservées après recharge dans `rejeu-original.json` ; analyse
`analyse-luna-originale.json`. Aucun changement du contrat d'opérations requis.

Le script conserve ces saisies et ajoute « Aubin, Brune est ici, dans le
refuge du relais. », puis la charge d'informer Brune que le fanal est dans
ce refuge. Cette information permet la perception ordinaire ; le devis de
la nouvelle charge est réalisable. Son jugement réel sans jet forcé est
accepté (`total=6`, `dd=4,033333`, `raison=adhesion`) et rechargé dans le
nouveau test. La première reprise Luna n'a pas transmis l'information
préalable ; le cas reste réalisable lorsque celle-ci est correctement typée.
Le banc enregistre désormais les charges du joueur depuis chaque sauvegarde
rechargée, permettant de lire les jugements réellement persistés. Bruts et
fin attendue : `reprise-integration/validation-references/fin.json` dans le dossier du lot.

Les résultats ci-dessous restent ceux de la livraison initiale.

**Invariant.** `mandat` passe par `echanges.confier` : accueil, devis, jet,
autorité perçue, dette, jugement et filiation communs. `agendas.charge_joueur`
fournit le parent de Corvus ; le compte rendu reprend le lot 283.
Un geste PNJ `confier` émet une offre ; `reponse_mandat` l'accepte ou la
refuse. Seul l'accord publie l'enfant, sans exécution forcée. Une voix inconnue
ou prétendue ne crée aucun mandant identifié. `bilan_mandat` est une parole,
pas une réussite physique ; le rendu distingue déclaration et réalisation.
Attributions/retrait 297 et ascendant 340 conservés, sans relations
subjectives imposées à Corvus. La façade des agendas valide ces données à
la recharge ; trois charges actives au plus, sans abandon choisi à sa place.

Schéma, fidélité et « Compris » étendus. Réponses moteur admises G15/G17 avant
publication ; fiche/comptes persistants ; aucun agenda privé au MJ. Les listes
`qui` passent par les références publiques. Le devis utilise une copie fermée
avec acteur neutre, sans capacités privées du joueur. Une date convenue reste
valide ; sans date ni durée calculable, aucune échéance n'est inventée.

**Tests consolidés : 169/169 verts, 17 fichiers**, aucune erreur ni saut,
dont les neuf méthodes du lot. Les scènes contrôlent monde, fiche, comptes,
vue et sauvegarde/recharge ; trois saisies passent par la vraie boucle avec
MJ simulé (deux charges et refus). Voix inconnue/prétendue réellement audible,
devis pur et indépendant des capacités privées, réaffectation couverts.
Première passe : 168/169, une erreur, 227,198 s. L'adaptateur du rejeu 86/87
complète l'ancienne carte des opérations ; archive, mots, contenus et
assertions conservés. Seul fichier repris : **11/11, 51,369 s**. Acquis des
seize autres réutilisés après contrôle des empreintes ; certificat
`tests-valides-final.json`. Échecs initiaux et erreurs de fixtures conservés.

**Empreintes : 8/8 paires identiques**, Relais/hameau, 2 h, graines
1985/7/42/2024, `fff9aab` → `9a8c204`. Chronique, mesures et état final
complet identiques nuit par nuit ; aucun plantage sur les seize nuits.
Usurpations et avis non justifiés **0 → 0**, avis à expliquer **5 → 5**.
Aucun mandat naturel : ces nuits prouvent la neutralité hors joueur actif.
Huit références exactes absentes calculées une fois et rangées dans le cache
commun ; aucune référence disponible relancée. Aucun gain de temps déduit.

**Luna : une passe**, trois tours/deux MJ/quatre appels, sans erreur technique,
mention sans fondement ou erreur de recharge. Typage `mandat` correct.
Échoppe inconnue de Corvus, même sous sa référence canonique : refus avant
parole, répété une fois par Luna. L'information est ensuite prononcée et
jugée irréalisable par Aubin sur ses croyances. **Aucun accord accepté** :
acceptation/exécution/compte rendu prouvés avec MJ simulé, pas par Luna.
Aucune seconde passe.

Suite détachée : **249,276 s**, deux travailleurs réduits au plus,
`validation-suite/fin.json` **ok=true**, codes tests/empreintes/Luna **0**.
Sources et tests encore identiques aux empreintes de validation à la clôture.
Aucun calcul actif ; ni suite complète ni fusion. Bruts conservés dans
`C:/Users/msics/donjon/artifacts/mandat-joueur-341/` : tests initiaux,
certificat consolidé, `validation-suite/empreintes.json`, fil Luna JSON/HTML,
`analyse-cloture.json` et `fin-cloture.json`.

**Limites.** Le choix autonome des mandataires d'A5 reste inchangé : ce lot
ouvre les gestes et paroles explicites avec le joueur, sans nouvelle
initiative PNJ ni sélection automatique de Corvus. Le protocole `informer`
du joueur porte ici les affirmations typées de lieu/verrouillage ; les avis
restent disponibles dans les mandats internes existants. Une déclaration
ne garantit jamais la réussite, ni un retrait l'arrêt d'une action volontaire
du joueur. La passe Luna ne certifie aucun accord accepté ; la garantie
est bornée aux scènes testées, sans prétention à couvrir toute formulation.
