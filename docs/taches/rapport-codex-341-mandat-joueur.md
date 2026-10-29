# Lot 341 — A5.9, le joueur mandant et mandaté

Branche `codex-mandat-joueur`, **non fusionnée**, base fournie `fff9aab`
(`origin/integration`). Dépendance 340 intégrée sans rebase par `82f5884` :
conflit documentaire seul, entrées des deux côtés conservées. `jeu.py` inchangé.

**Invariant.** Une parole typée de Corvus confie une charge `amener` ou
`informer` par `echanges.confier` : même accueil, devis, jet, autorité perçue,
dette, jugement enregistré, filiation et compte rendu que pour un PNJ.
`agendas.charge_joueur` fournit le parent explicite ; confirmations et bornes
de filiation restent communes. Les charges de Corvus sont conservées par la
façade des agendas, validées à la recharge, sans lui créer un esprit autonome.
La limite de trois charges actives refuse une nouvelle charge au joueur au
lieu de choisir à sa place laquelle abandonner.

Un geste PNJ `confier` vers Corvus émet une offre déterministe qui attend son
accord. La réponse typée `reponse_mandat` accepte ou refuse cette offre
entendue ; seule l'acceptation publie l'enfant et les attributions communes.
Elle ne déplace personne et n'exécute aucune mission. Une voix inconnue ou
seulement prétendue ne fournit aucun mandant identifié. `bilan_mandat`
enregistre une déclaration d'issue : le jugement du destinataire reste celui
du compte rendu 283, sans réalisation fictive. Le rendu distingue une issue
déclarée d'une réalisation connue. Suivi et retrait utilisent les attributions
297 ; ascendant des PNJ envers Corvus : mécanisme 340, sans relations
subjectives imposées au joueur.

Schéma et contrôle de fidélité des paroles étendus ; `comprehension.contenu`
rend ces actes dans « Compris ». Les réponses fixées sont admises par G15/G17,
avant affichage et sauvegarde. Fiche, comptes et contexte ne publient que les
charges de Corvus et les offres reçues, jamais les autres agendas des PNJ.
Les listes `qui` passent par le contrôle commun des références publiques.
Le devis du joueur utilise un acteur neutre dans une copie fermée du mandant,
sans lire ses caractéristiques privées. Une date explicitement convenue est
conservée ; sans date ni durée calculable, aucune échéance n'est inventée.

**Tests consolidés : 169/169 verts, 17 fichiers**, aucune erreur ni saut,
dont les neuf méthodes du lot. Les scènes contrôlent monde, fiche, comptes,
vue et sauvegarde/recharge ; trois saisies passent par la vraie boucle avec
MJ simulé (deux charges et refus). Voix inconnue/prétendue réellement audible,
devis pur et indépendant des capacités privées, réaffectation couverts.
Première passe : 168/169, une erreur, 227,198 s. Le rejeu 86/87 fournissait
l'ancienne carte des opérations ; son adaptateur complète le schéma courant
sans modifier l'archive, les mots, les contenus ou les assertions historiques.
Reprise du seul fichier : **11/11, 51,369 s**, paroles, ordre et recharge
conservés. Consolidation sans nouvelle exécution des seize autres fichiers ;
empreintes du code du jeu et des tests inchangés contrôlées.
Preuve : `tests-valides-final.json`. Le bilan brut initial `ok=false` reste
intact. Les erreurs de fixtures et de temporaires des passes de travail
restent également archivées.

**Suite de validation détachée, résultats à relire.**
`tools/valider_mandat_joueur_341.py` réemploie les tests consolidés après
vérification de leurs empreintes, puis joue huit paires d'empreintes 2 h
(Relais/hameau, quatre graines) et **une passe Luna** sur
`tests/data/bancs/mandat-joueur.json`. Référence exacte de la base fournie,
résultats réemployés dans le cache commun ; les références absentes sont
calculées une fois. Deux travailleurs réduits au plus, calcul détaché,
`fin.json` écrit en dernier, empreintes des sources contrôlées. Ni suite
complète, ni campagne de modèles. Bruts et fin attendue :
`C:/Users/msics/donjon/artifacts/mandat-joueur-341/validation-suite/fin.json`.

**Limites.** Le choix autonome des mandataires d'A5 reste inchangé : ce lot
ouvre les gestes et paroles explicites avec le joueur, sans nouvelle
initiative PNJ ni sélection automatique de Corvus. Le protocole `informer`
du joueur porte ici les affirmations typées de lieu/verrouillage ; les avis
restent disponibles dans les mandats internes existants. Une déclaration
ne garantit jamais la réussite, ni un retrait l'arrêt d'une action volontaire
du joueur. Les empreintes passives et la passe Luna restent à analyser avant
de déclarer la vérification du lot terminée.
