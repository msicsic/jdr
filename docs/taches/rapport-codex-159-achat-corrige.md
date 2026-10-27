# Lot 159 — Source des pièces et correction d'achat

Branche `codex-achat-corrige`, non fusionnée, base `7adc788`. Aucun changement
de `main`, de l'assemblage des requêtes, des fournisseurs, des consignes ni du modèle Luna.

**Cause et invariant.** Le fil `soir-appel` p1 n°5 du lot 153 donne
`contrepartie={type:pieces,montant:3,objet:planches}`, puis la correction conserve
le champ avec `planches de bac`. Le refus ancien exige seulement un objet à
pièces ; le schéma autorise `objet` sans décrire son rôle ni l'alternative sans
ce champ. La validation n'est pas trop stricte : ce champ choisit la source des
pièces et ne peut désigner le bien acheté. Le contrat doit distinguer les deux
rôles et fournir une correction exacte sans perdre le montant.

**Changement.** `propositions.schema_terme` décrit la source facultative des
pièces. `propositions.verifier` garde le refus et fournit le chemin, la valeur,
le sens du champ et le terme exact accepté après retrait du seul `objet`.
Le module commun porte ces deux contrats ; aucun assemblage de schéma dans
`mj._echanger` n'est modifié. Aucun effacement automatique, paiement ou parole
sur une proposition refusée. Le paiement ordinaire, la fidélité et les droits
restent contrôlés. Le contrat MJ est précisé.

**Preuves.** Cinq tests ciblés verts (22,37 s), dont un nouveau parcours double
console/MJ simulé : achat réel d'une planche d'Aubin, autre achat d'une bûche de
Joss. La source erronée est refusée sans mutation ; la correction sans source
paie le même montant, détache une part, puis la livraison est portée et visible
dans la fiche après sauvegarde/recharge. Le refus vérifie champ, valeur reçue
et correction exacte. Les premiers essais en bac à sable ont échoué sur les
permissions des dossiers temporaires ; reprise autorisée hors bac à sable verte.
Suite complète unique : **2 199 tests, 249 fichiers, 16 ignorés, zéro erreur,
3 échecs bruts, 3 844,17 s**, un travailleur réduit pour cohabiter avec
la suite d'intégration et respecter le plafond du poste ; vérification au-delà
du créneau du lot.
Le fichier de stabilité du préfixe a deux sous-tests en échec : référence figée
`4641dc3` déjà périmée sur les instructions et l'entrée. Deux scènes rejouées
sur une copie intacte de `7adc788` : seuls le schéma de l'audit atelier et sa
description changent avec ce lot ; état, rendu, instructions et entrées sont
identiques à cette base. Empreintes actualisées après ce contrôle ; **neuf tests
de stabilité repris verts** (6,17 s), sans seconde suite complète.
Le troisième échec, `test_mesure_prompt.test_identique_au_fournisseur_sans_reseau`,
est reproduit sur la copie intacte de `7adc788` (trois tests, un échec, 0,08 s) :
la clé de cache attendue par l'outil omet `:interpreter`. Défaut préexistant
hors périmètre laissé signalé ; **un échec historique restant**, aucune
régression connue du lot après reprise ciblée.

**Luna, une passe.** Trois scripts, copies seulement, ChatGPT medium/libre,
budget 200, une exécution réduite. Référence p1 `cdaf371` relue dans les archives
du lot 153, SHA-256 conformes à son manifeste (cache d'origine absent ici).
Appels/tour référence → branche : soir-appel **4,00 → 4,50**,
ressources **4,67 → 4,00**, noms-dialogue **3,25 → 3,75** ; total **43 → 45**
appels sur **11 tours**, **3,91 → 4,09**. Aucun repli, refus moteur/contre-revue,
arrêt technique ou erreur de recharge sur la branche. Achat n°5 exécuté en six
appels, trois pièces remises, part encore due ; n°6 `planches_1` portée après
recharge. Le premier typage est valide, sans correction naturelle du N11.
Pas de conclusion de vitesse : charges historiques différentes.

**Limites et livraison.** La correction de Luna et la fidélité restent
sémantiques ; aucune garantie pour toute saisie libre. Le parcours historique
de source invalide est exercé par simulation, pas réémis par Luna dans cette
passe. Le harnais conserve les projections rechargées ; les tests contrôlent
le monde et le rendu. Un premier lanceur cherchait une clé historique absente
et a commencé une référence : arrêté sans partie achevée, worktree temporaire
supprimé, aucune référence rangée ; branche jouée une seule fois ensuite.
Aucune clé Git de signature configurée : commit non signé, branche seule
poussée, sans fusion. Bruts : `artifacts/mesures-159.json`,
`artifacts/bancs-multi/20261027-024400-25724/`, journaux `artifacts/*159*.log`.
