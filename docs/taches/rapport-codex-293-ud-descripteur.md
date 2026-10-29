# Lot 293 — U-D : identité du geste au clic

Branche `codex-ud-descripteur`, base intégration `8acbbd9`, non fusionnée.

## Changement et invariant

Un clic d'objet ou de porte transmet `{geste, cible, parametres?}`,
avec la référence publique déjà fournie par la scène. La marche du clic et
« Regarder par là » transmettent aussi un descripteur. La page conserve
l'approche pas à pas ; elle ne reçoit ni règle de faisabilité ni donnée nouvelle.

`commandes.DescripteurPublic` est indépendant du web. `Moteur.preparer`
reçoit cette entrée, en vérifie la forme et la référence exacte encore perçue,
puis emprunte son validateur habituel. Aucun nom ou alias n'est recherché ;
une référence opaque continue à désigner le même corps. Une cible disparue ou
hors de vue est refusée publiquement, sans viser un homonyme. Les seuls
paramètres actuels sont `outil` et `methode` : ils ne fixent aucun effet.
`geste_local` partage la construction canonique avec les commandes, y compris
la séquence moteur de `manger`.

Le serveur et `PontWeb` transportent une saisie **ou** un descripteur. La boucle
`jeu.py` devait être adaptée : elle n'acceptait que des chaînes. Son exécution
locale est extraite dans `executer_local`, partagée avec le texte, avec les
confirmations existantes, la sauvegarde avant affichage et le résultat G4.
Le descripteur arrive avant toute analyse, compilation ou revue du MJ ; tout
préalable manquant reste un refus du moteur. Aucune branche du MJ ni mécanique
PNJ n'est modifiée.

## Vérification et mesures

Les tests exercent les neuf gestes d'objet et les cinq gestes de porte : même
plan, état complet, texte public et vues après recharge ; deux cibles homonymes,
référence absente, hors de vue, geste devenu impossible. Deux suppressions
réelles après construction du menu sont également vérifiées. Le journal
attribue au joueur le plan exact choisi ; les PNJ continuent à vivre pendant
sa durée. Clé et outil explicites passent par les mêmes paramètres. Le parcours
HTTP réel contrôle prise, rotation, refus périmé et recharge, avec l'analyseur
et le MJ interdits. Une scène cachée et un personnage inconnu sans portrait
contrôlent la projection et les références publiques.

Les tests Node existants attendent désormais un descripteur au lieu du texte
pour les gestes ; leurs assertions de portée, chemin et touches sont conservées.
La sonde exécute aussi les callbacks et vérifie le corps effectivement envoyé.

Bilan retenu : **70 tests / six fichiers, tous verts**, zéro erreur ou ignoré,
448.460 s cumulées. Les 28 tests TUI sont inchangés. Cinq fichiers
verts du bilan `tests-final.json` et le nouveau fichier intégral de
`tests-descripteur-final.json` sont réunis dans `fin-cloture.json`. Aucune suite complète.
Les essais initiaux de nouvelles scènes avaient des oracles incorrects
(perception initiale, vie des témoins), corrigés sans changement moteur. Le
premier lancement sous bac à sable refusait les fichiers temporaires ; les
vérifications avec accès au disque sont conservées.

Mesure sans réseau sur la vraie boucle du `jeu.py` de la base et celle du lot,
avec MJ instrumenté : **14 couples famille/geste + marche + rotation :
0 → 0 appel au modèle**, mêmes sorties publiques. Déverrouiller sans clé et
crocheter sans outil : deux refus publics, **0 → 0 renvoi pour préalable
manquant**. Sur un cas supplémentaire sans portrait, l'ancien clic « examiner »
renvoyait au MJ (un `echanger`, appels internes non mesurés) ; le descripteur
reste moteur, zéro appel. Dix-sept cas au total, `fin-mesures.json` : `ok=true`.

## Limites et livraison

Le clic annonce un verbe, sans promettre sa réussite. Les outils ne sont pas
ajoutés au menu ; U-M garde ce travail. **« Lui parler » est inchangé** : saisie
`parler <référence publique>`, conversation libre pouvant appeler le MJ.
Les touches et la saisie textuelle restent sur leurs voies actuelles ; U-T/U-P
restent à faire. Pas de passe Luna : aucun chemin du modèle n'est modifié.
Pas de banc PNJ : l'entrée de l'interface seule change.

Bruts et sonde : `C:/Users/msics/donjon/artifacts/ud-293/` (`mesures.json`,
`fin-mesures.json`, bilans de tests et trace de suppression). Aucun calcul long
lancé. Fusion et suite complète laissées au superviseur.
