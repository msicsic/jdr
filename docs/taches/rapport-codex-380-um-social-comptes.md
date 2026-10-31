# Lot 380 — U-M social comptes

Branche `codex-um-social-comptes`, base `integration 85052cf8`, PC fixe.
**Bilan initial validé le 2026-10-31, non fusionné. Code initial vérifié : `168ee1f2`.**

**Reprise de fusion validée le 2026-10-31. Code vérifié : `643b77f5`.**
`origin/integration 3999bb3a` est fusionné dans la branche pour réunir comptes
et avis (386/389). Les styles, projections,
boutons, réinitialisations et sondes Node des deux formulaires sont conservés ;
leurs descripteurs et validateurs restent distincts. Une régression soumet les
deux formulaires depuis le même état public et contrôle leurs termes propres.
**62/62 tests verts en 599,135 s**, sept fichiers, zéro échec, erreur ou saut :
comptes (11), inventaire (7), descripteurs (10), avis web (5), avis terminal (8),
information (12) et web (9). Les callbacks réels de `clic_page.js` sont exercés
par ces parcours ; son contrôle Node réussit aussi.
**Empreintes Relais 2 h × quatre graines : 4/4 identiques** à `3999bb3a`,
chronique, mesures et état final complet ; aucun plantage. Les quatre nuits de
référence ont été calculées puis rangées au cache ; aucune référence relancée.
`reprise-integration-3999bb3a/fin-verification.json` : **`ok=true`** ; les quinze
fichiers de `sources.json` correspondent encore aux sources livrées.
Les mesures suivantes sont le bilan historique de la livraison avant fusion.

**Invariant.** Le formulaire web fige un choix public complet : débiteur,
créancier, montant, objet ou termes de l’offre déjà proposée à Corvus.
Ses lignes sont celles de `biens.comptes_joueur` ; les choix structurés utilisent
les seules créances apprises et les prêts reçus par Corvus, plus ses offres publiques.
Aucune bourse privée, dette entre tiers ou créance non apprise n’est envoyée.
Préparer ou annuler ne transfère rien. La question sur le dû garde la mécanique
existante de `reclamer` : elle peut conduire à un règlement, après confirmation.

**Raccord.** `dialogues.comptes_publics` fournit libellés et descripteurs ;
`valider_choix_compte` vérifie leur égalité JSON stricte avec les choix actuels,
y compris les types numériques. Les créances passent par la parole directe
existante, les offres par `conversation_pnj/accepter`, avec une adresse interne
revalidée et des termes complets dans l’aperçu. Le moteur tranche l’accord,
les paiements partiels ou refusés ; G17 enregistre ses mots avant affichage.
`offre_mission` renvoie désormais aucune prime pour un marché sans mission :
le récapitulatif commun ne doit pas chercher une mission inexistante.

La restitution utilise la remise ordinaire. `commandes.py` valide le compte
public avant de transmettre le geste ; un accord rémunéré concurrent entraîne
un refus, pour éviter de remplacer la restitution choisie par une vente.
La famille entière `remettre` rejoint U-C dans `moteur.py`, clic et commande
typée compris : aperçu, confirmation et état inchangé requis. Le rendu moteur
dit « restituer » lorsqu’un prêt est effectivement rendu. Aucun changement de
`jeu.py`, `tui.py`, du modèle, de l’autonomie ou des registres d’esprit par le lot 380.
Recouvrement potentiel avec le lot 375 : `commandes.py` et `moteur.py` ; aucun
fichier de position crue (374) ou de mémoire (378) modifié.

**Épreuves et mesures initiales. 77 tests distincts sur huit fichiers, tous verts : zéro
échec, erreur ou saut.** `tests-finaux.json` : **27/27 en 250,128 s**, dont les
dix méthodes du lot, inventaire et descripteurs. Cinquante voisins supplémentaires
retenus de `voisins-premiere.json` (**67/67 en 979,216 s**, dix-sept doublons
exclus du comptage) : E5, G17, U-C, information et web.
Les dix méthodes ciblées couvrent vrais callbacks Node, créances
d’Aubin et Brune, paiement/refus, question sans dette, deux prêts homonymes
restitués séparément, deux offres et prix distincts, manque d’argent, annulations locales
et U-C, injections et comptes périmés. La vraie boucle vérifie zéro appel au
modèle et sauvegarde avant affichage ; parité avec les transactions typées,
monde, émissions, fiche, regard et scène après recharge. Le laps entier ou
découpé utilise l’avancement réel des PNJ avec recharge intermédiaire : comptes
et ressources sont comparés ; chaque état et ses vues sont vérifiés après recharge.
Cela ne prouve pas l’identité de tous les messages ambiants entre découpages.
Quatre clics de formulaire, puis une confirmation ; temps humain non mesuré.

Adaptation voulue de `test_inventaire_public` : la remise exige maintenant
« tenter ». Les assertions de transfert, homonymie et vues sont conservées ;
la confirmation et la garde d’état sont ajoutées. Seul le transport du clic
diffère du plan typé, contrôlé séparément. Le harnais commun accepte cette
confirmation explicite, sans confirmer automatiquement les autres gestes.
**Empreintes 2 h, quatre graines, Relais et auberge : 8/8 identiques** à la base
`85052cf8`, chronique, mesures et état final complet ; aucun plantage.
Quatre nuits de référence relues du cache, quatre calculées et rangées ; huit
nuits de branche jouées. Aucune comparaison de temps entre ces références.
`fin-verification.json` : **`ok=true`** ; les neuf empreintes de `sources.json`
correspondent encore aux fichiers livrés. Les passes rouges restent archivées,
dont le `KeyError` de prime corrigé plus haut et l’exploration des prêts sortants.

**Limites et livraison.** Selon l’arbitrage explicite de l’utilisateur, aucun
remboursement volontaire d’une dette en pièces n’est ajouté au formulaire 380 ;
le moteur de ce remboursement est depuis porté par le lot 388 dans l’intégration.
« Restituer » rend un prêt ; « régler » accepte une offre déjà publique,
sans créer un éditeur de marché ni une nouvelle offre. Pas de Luna ni de suite
complète. Prêter un objet de Corvus à un PNJ n’est pas une voie admise par les
validateurs actuels ; son portage reste aussi hors lot. Le test exploratoire
qui l’a révélé est conservé dans les bruts ; aucun validateur n’est assoupli.
Deux travailleurs réduits au plus ; reprise de fusion validée, aucun calcul restant.
La branche est poussée sur `origin` ; les limites concernent le périmètre du formulaire 380.
Synthèse initiale : `cloture.json` ; synthèse de reprise : `reprise-integration-3999bb3a/cloture.json`.
Bruts et lanceur : `C:/Users/msics/donjon/artifacts/um-social-comptes-380/`.
Fusion et vérification d’intégration laissées au superviseur.
