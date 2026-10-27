# Lot 180 c — Comptes moteur, répliques seules comparées

27 octobre 2026 — Branche `codex-comptes-ecrits-moteur`, **non fusionnée**.
Base initiale `e61cf08`, correction c sur `a0fcdb5` après b (`885b1c5`).

**Invariant.** Le narrateur ne dit aucun compte ; le moteur écrit le compte,
ou une réplique compatible l'évoque. `comptes_narratifs.controler` refuse
strictement les assertions comptables du narrateur, sans comparaison sémantique
de sa paraphrase. Seules les citations de PNJ passent `lire/compatibles` :
montant, sens, état et conditions contre l'issue et les offres typées. Une
quantité présentée sans prédicat n'invente pas un transfert ; le deux-points
sépare sa proposition de l'explication qui suit. Les compléments de lieu
contenant « pièce » ne sont pas des monnaies. La règle de narration dit ce
partage d'autorité en une règle commune, sans exception de scénario.

**Rendu.** `phrases` écrit des phrases naturelles à la deuxième personne,
avec désignations publiques sans apposition et accords de `francais`.
Paiement et livraison réciproque sont réunis ; un remboursement ne répète
pas son solde nul et l'offre conclue ne répète pas l'issue déjà affichée.
`paroles.preparer_parole` relie les textes des opérations à leurs effets
comptables typés ; `completer` remplace ces anciens textes techniques tout
en gardant les faits des autres opérations de la même parole. Les métadonnées
grammaticales des parts et services viennent des biens et engagements, sans
changer leur mécanique. `mj` utilise le même formateur pour les offres
préparées et affichées. Preuve exacte, contrôle avant enregistrement et repli
restent communs. Aucun fichier réservé au lot 179 n'est modifié.

**Vérification c sans Luna.** **2 289 tests, 264 fichiers, 1 382,257 s** :
uniquement les deux échecs MiMo historiques `6 != 5`, zéro erreur ni ignoré.
Tous les tests du lot sont verts, dont les six nouveaux tests de rendu naturel.
Une seule suite complète, deux travailleurs à priorité réduite ; aucune reprise
nécessaire après celle-ci.
Console/MJ simulé et recharge : quatre narrations comptables réelles refusées,
Gorm/Aubin remboursés, Brune encore débitrice, réplique présentative réelle
admise, prime de vingt conservée et prime inventée refusée, achat de planches
et autre achat de parts, pied-de-biche « dans cette pièce » et autres salles.
Les nouveaux tests contrôlent le texte moteur mot pour mot, l'état sauvegardé
et le rendu rechargé ; une parole à plusieurs opérations conserve ses faits
non comptables. Les tests du lot couvrent aussi absence de dette, inversion,
montants, rôles et objet de condition incompatibles.

**Mesures externes de b**, laptop, transmises par l'orchestrateur : `a0fcdb5`
contre `cdaf371`, comptes en deux passes : appels/tour 5,08 → 4,58,
secondes/tour 19,5 → 17,6 ; comptes justes, prime rétablie, mais replis 1 → 2.
Références en une passe : relances 3 → 6, refus 8 → 13. Ces faux refus et
le rendu technique ont motivé c ; ces mesures ne valident pas c.

**Limite.** La grammaire de détection et de comparaison reste bornée, sans
compréhension universelle du français. Les assertions implicites ou complexes
hors de cette grammaire peuvent encore échapper au contrôle ou rester ambiguës :
l'invariant exhaustif en langue libre n'est pas garanti. Aucun gain Luna
propre à c n'est certifié ; sa validation reste à jouer par l'orchestrateur.

**Livraison.** Aucun Luna joué. Commandes exactes dans
`C:/Users/msics/donjon/artifacts/comptes-180/luna-a-jouer.txt` : deux passes
comptes/soir-appel/ressources/echanges, une passe relais/crypte/atelier,
contre `cdaf371` en cache. Tous les bruts sont dans ce dossier, accessible
par la jonction ignorée `artifacts/`. Pas de clé de signature configurée :
commit non signé sur cette seule branche, sans fusion.
