# Lot 207 — Réclamer le bien spolié

Branche `codex-reclamer-vol`, **non fusionnée**, base `c6c2de6` vérifiée.
Aucun Luna ; au plus deux travailleurs, priorité réduite. Bruts exclusivement
`C:/Users/msics/donjon/artifacts/reclamer-207/`. Aucune clé Git de signature
configurée : commit non signé, livraison sur la branche seule.

**Invariant.** Avant la recherche de reprise, `agendas.planifier` appelle
`pnj_propositions.reclamation` : geste social `demander`, contenu `reclamer`,
porteur et présence crus, sans peur, danger connu ni inconscience crue.
Ce recours reste hors graphe. Contact/audition et refus communs sont revalidés ;
la reprise reste soumise aux coûts de faute/violence existants.

`echanges.demander`, commun au joueur et aux PNJ, pèse la rétention illégitime
par `prix_faute(ARGENT)` et `valeur_proposition` ; méfiance, rancune, utilité
gardent leurs causes. Le prêt autorisé conserve son contrat. `remettre`
enregistre possession/croyance ; l'actualisation atteint le projet. Le joueur
reçoit la demande avec attente enregistrée, sans restitution imposée.
**Autorisation du superviseur** : adaptation du seul rendu des refus dans
`paroles._reclamer`, sans consigne ni contrôle narratif. Aucun autre interdit touché.

**Cas réel.** La base actuelle ne reproduit plus la naissance de crue 7.
Sur **9904574**, capture à 151, naissance à **152**, atteint à **228** et bûches
réellement chez Gorm. Même capture rechargée avec la branche : réclamation à
**213**, refus **rancune**, sommeil sans plan admissible ; bûches chez Brune.
Captures 151/240 conservées ; **89 minutes entières/découpées, monde/rendu
et recharges identiques**. Copies isolées supprimées.

**Preuves.** Dix nouveaux tests verts, **9,262 s** : restitutions autonomes du
ballot Anselme/Lucien et du marteau Gorm/Brune ; refus puis reprise après dépôt
ou violence contrôlée ; joueur qui rend par `Moteur` ou garde ; exclusions ;
temps entier/découpé, monde/rendu rechargés et causes affichées. La violence
autonome reste interruptible par bruit/secours.

**Suite unique : 2 411 tests / 279 fichiers, 3 117,025 s**, sept assertions en
échec, zéro erreur, 16 ignorés. Quatre méthodes rejouées sur `c6c2de6` : seul
`test_rondes_resumees` échoue déjà. **Dix reprises finales vertes, 10,710 s** :
portage puis refus et identité explicitée ; réception des accusations isolée
de la réclamation prioritaire, sans relâcher ses assertions. Les dix nouveaux
tests et la capture gardent les réclamations actives. Sommeil et restitution
acceptée ont aussi leurs conditions explicites. **Bilan : un échec préexistant**,
aucune seconde suite complète ; vérification au-delà du créneau.

**Banc 4 h, vingt paires** : cinq scénarios × 1985/7/42/2024, vingt références
relues du cache **a488f1f**, code `donjon/` et `tools/` identique à `c6c2de6`.
Zéro plantage/usurpation ; **20/20 chroniques identiques**, 9/20 empreintes
complètes identiques ; les réponses entendues ont un rendu enrichi, sans
attribution exhaustive des onze écarts d'état. Compteur d'avis identique :
**57 non justifiés, 272 à expliquer, 563 cycles accomplis**, aucune boucle
nouvelle mesurée. Réclamations de vol, restitutions et reprises de projet :
**0 → 0**, aucune naissance de récupération sur cette base. La garde finale
d'inconscience, vérifiée en ciblé après ce banc, ne s'exerce donc dans aucune
de ces nuits ; aucun rejeu inutile. S/F/D du lot 183, fonction `cats` inchangée,
PNJ inactifs inclus, moyennes avant = après :

| Relais | Mine | Auberge | Crue | Hameau |
| --- | --- | --- | --- | --- |
| 11,25 / 4,5 / 1,813 | 21,5 / 4,25 / 1,643 | 11,25 / 4 / 0,906 | 23,75 / 6,75 / 2,813 | 27,25 / 6,75 / 2,333 |

**Limites.** Aucun gain naturel de richesse démontré sur ces vingt nuits ;
preuves de la nouveauté en scènes et capture historique. La parole utilise
encore la salle commune du contrat social actuel. Rachat au voleur,
dénonciation et extension de la perception sociale hors lot ; aucune garantie
générale contre toutes les boucles. Temps du cache non comparés à la branche.
