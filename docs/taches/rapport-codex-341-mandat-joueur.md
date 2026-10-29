# Lot 341 — A5.9, le joueur mandant et mandaté

Branche `codex-mandat-joueur`, **non fusionnée**, base fournie `fff9aab`
(`origin/integration`). **Lot terminé**, moteur `113d15a`, validation `9a8c204`,
branche poussée. Dépendance 340 intégrée sans rebase par `82f5884` : conflit
documentaire seul, deux côtés conservés. `jeu.py` inchangé.

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
