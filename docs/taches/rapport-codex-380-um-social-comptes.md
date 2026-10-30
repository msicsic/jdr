# Lot 380 — U-M social comptes

Branche `codex-um-social-comptes`, base `integration 85052cf8`, PC fixe.
**Implémentation livrée ; vérification finale en cours, non fusionnée.**

**Invariant.** Le formulaire web fige un choix public complet : débiteur,
créancier, montant, objet ou termes de l’offre déjà proposée à Corvus.
Ses lignes sont celles de `biens.comptes_joueur` ; les choix structurés utilisent
les seules créances apprises et les prêts de Corvus, plus ses offres publiques.
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
`jeu.py`, `tui.py`, du modèle, de l’autonomie ou des registres d’esprit.
Recouvrement potentiel avec le lot 375 : `commandes.py` et `moteur.py` ; aucun
fichier de position crue (374) ou de mémoire (378) modifié.

**Épreuves.** Dix méthodes ciblées couvrent vrais callbacks Node, créances
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
La première passe rouge révélait le `KeyError` de prime décrit plus haut ;
elle reste archivée. Les résultats définitifs et empreintes 2 h × quatre graines,
Relais et auberge, sont attendus dans `fin-verification.json` : ne pas déclarer
ce lot vérifié tant que son champ `ok` n’est pas vrai.

**Limites et livraison.** Selon l’arbitrage explicite de l’utilisateur, aucun
remboursement volontaire d’une dette en pièces n’est ajouté : piste d’un lot
séparé. « Restituer » rend un prêt ; « régler » accepte une offre déjà publique,
sans créer un éditeur de marché ni une nouvelle offre. Pas de Luna ni de suite
complète. Prêter un objet de Corvus à un PNJ n’est pas une voie admise par les
validateurs actuels ; son portage reste aussi hors lot. Le test exploratoire
qui l’a révélé est conservé dans les bruts ; aucun validateur n’est assoupli.
Deux travailleurs réduits au plus ; calcul final détaché.
Bruts et lanceur : `C:/Users/msics/donjon/artifacts/um-social-comptes-380/`.
Fusion et vérification d’intégration laissées au superviseur.
