# Lot 214 — Racheter son bien au détenteur

Branche `codex-racheter-bien`, **non fusionnée**, base `cca5f50` vérifiée.
Code `2b47bd9`, commit non signé : aucune clé Git configurée. Aucun Luna.
Deux travailleurs au plus, priorité réduite ; bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/racheter-214/`.

**Invariant.** Le seul geste d'achat de `planification.gestes` admet le rachat
au détenteur : mêmes budget, coût et refus (`offre_refusee` dès la génération
et à l'exécution). `echanges.demander` conserve la restitution gratuite du
détenteur honnête ; vendre exige que le gain dépasse le prix de faute commun
`prix_faute(ARGENT)`. Accueil, utilité, garde et prix restent ceux de la vente.
Paiement/remise, propriété, permissions et croyances précèdent le récit ;
l'actualisation ordinaire atteint le projet. Aucune constante changée.

**Preuves.** **29 ciblés verts**, dont sept nouveaux (23,001 s). Réclamation
refusée puis rachat autonome : ballot Anselme/Lucien et marteau Gorm/Brune.
Scènes d'auteur : estimation initiale 70, revente 7 ; trois minutes entières
ou découpées, monde/rendu rechargés identiques, paiement unique, permissions
closes, projet atteint. Refus retenu sans répétition, pauvreté, retour gratuit
et prix insuffisant couverts. Joueur acheteur par sa parole `demande`
existante : bourse, propriété et réponse affichée relues après sauvegarde.
**Bois du guet**, scène d'auteur équivalente : réclamation refusée, achat
disponible mais coût **5,944 > poids 1,857432** ; projet en sommeil, bois chez
Brune, laps découpés et recharges identiques (`bois-auteur.json`). Aucun
plafond changé. Capture historique 207 à 151, rejouée 89 minutes : égalité
entier/découpé/rechargé ; sur cette base, aucune naissance de récupération,
bois au guet à 240 (`captures.json`), pas de rachat naturel démontré.

**Mesures.** Suite unique : **2 429 tests / 281 fichiers**, zéro échec/erreur,
16 ignorés, **3 580,295 s**. Banc **20 paires 4 h** : chroniques et états
complets **20/20 identiques**, zéro plantage/usurpation, aucune nouvelle
alerte. Compteur 199 inchangé : **24 non justifiés / 204 à expliquer / 510
cycles accomplis**. Naissances de récupération, réclamations de biens,
rachats et reprises de projet : **0 → 0** ; les trois « réclame » sont des
dettes monétaires. S/F/D du lot 183, PNJ inactifs inclus, avant = après :

| Relais | Mine | Auberge | Crue | Hameau |
| --- | --- | --- | --- | --- |
| 10 / 4 / 1,563 | 22 / 4,25 / 1,607 | 11,25 / 4 / 0,906 | 23 / 6,75 / 2,625 | 29,5 / 7,5 / 2,292 |

Coût mine fixe 1985, 4 h (`mesure_cout.py`) : tous compteurs identiques,
**870 recherches, 10 624 nœuds, 67 943 gestes** ; aucun surcoût en recherche.
`main` local étant ancien et aucune référence équivalente en cache, base
exacte `cca5f50` calculée une fois puis cachée ; branche figée `2b47bd9`.
Temps du cache non comparés. Vérification au-delà du créneau ; aucune
seconde suite complète, aucun fichier des lots voisins modifié.

**Limites/raccord joueur.** La réclamation passe avant le rachat ; prix
déclaré et poids du projet le bornent, aucune surenchère nouvelle. Le bois
historique n'a pas de prix entier déclaré ; celui de la scène est explicite.
Le raccord autorisé dans `moteur.py`/`dialogues.py` aurait nécessité un nouveau
parcours, l'acceptation existante ne visant que les missions. **Joueur vendeur
hors lot selon le repli demandé**, aucun raccord réalisé, aucune commande
ni obligation ajoutée. Aucun gain naturel de richesse ni garantie générale
contre toutes les boucles démontré.
