# Lot 399 — Rembourser depuis les comptes publics

Branche `codex-rembourser-public`, issue d’`integration 60f857c5`,
départ du lot `561c1d16` (brief), PC fixe, 31 octobre 2026.
**Code réalisé ; vérification groupée détachée en cours, non fusionné.**

**Invariant.** Chaque dette personnelle en pièces déjà affichée par
`biens.comptes_joueur` fournit un choix « Rembourser ». Les lignes d’un même
créancier sont cumulées ; le solde entier est proposé, un montant partiel
est possible. La présence du créancier ne conditionne pas la projection :
le moteur donne le refus du 388 s’il est absent. Aucun compte privé,
fonds d’autrui ni dette non apprise envers Corvus n’est exposé.

`dialogues.comptes_publics` produit le même descripteur U-D pour les trois
interfaces. Seul `parametres.montant` est éditable ; l’égalité JSON stricte
des autres termes, types numériques compris, protège le solde public figé.
`parole_compte` prépare la parole typée `rembourser` du 388. Un essai de
`biens.rembourser_dette` sur copie conserve ses refus distincts avant les
gardes de parole ; la transaction U-C rejoue et revalide avant tout transfert.
Préparer, annuler ou abandonner ne verse rien et ne publie aucune parole.

Le web ajoute un champ numérique prérempli. `ComptesTerminal` demande le
montant après le numéro ; Entrée conserve le montant proposé. Console et TUI
acceptent cette entrée vide seulement quand le formulaire l’annonce.
Le pont web transmet déjà la projection commune : aucun changement nécessaire
dans `pont.py`. Aucun changement du modèle, des mécaniques du 388, de
l’autonomie ou des registres d’esprit.

**Preuves obtenues. Douze nouveaux tests verts** : neuf en **170,802 s**,
puis trois compléments en **66,679 s**, sur les mêmes sources de production.
Vrais callbacks JavaScript, boucle console et pilote Textual : remboursement
total à Brune, partiel à Gorm (`marchand`), mêmes résultats que la parole
typée du 388 ; monde, bourses, comptes, émissions, fiche, regard et scène
comparés après recharge. Laps réel entier 60 dixièmes contre 13/29/18 avec
recharges intermédiaires ; le contrôle de parité typée couvre aussi 120 contre
40/80. Annulation locale et U-C, montant invalide, injections, compte périmé à
réception ou confirmation, créancier parti et fonds perdus avant confirmation
sont exercés. Les harnais interdisent le modèle et contrôlent la sauvegarde
avant publication. Les assertions de sécurité anciennes sont conservées.
Seule attente remplacée : l’absence du raccourci dans le test du 396, devenue
incompatible avec le brief 399 ; le test vérifie désormais sa dette personnelle
et garde ses contrôles de confidentialité. Les helpers acceptent le montant.

**Empreintes : 8/8 paires identiques**, chronique, mesures et état final complet,
sans plantage : Relais/auberge, 2 h, graines 1985/7/42/2024, référence `561c1d16`.
Huit références manquantes calculées une fois puis rangées au cache commun ;
aucune comparaison de performance revendiquée. Contrôle Node et diff propres.

**À reprendre.** Neuf fichiers ciblés et voisins tournent avec deux travailleurs
réduits ; `fin-verification.json`, écrit en dernier, vérifie tests, empreintes
et identité des sources. Consulter ce bilan avant de déclarer le lot validé.
Pas de suite complète ni de Luna. Le versement reste soumis aux préconditions
du 388 ; aucune nouvelle mécanique comptable ni éditeur de marché.
Bruts et lanceur : `C:/Users/msics/donjon/artifacts/rembourser-public-399/`.
Les premiers refus de permissions Windows et erreurs d’import du harnais
n’ont pas modifié le jeu ; les reprises et leurs journaux sont conservés.
Fusion et vérification d’intégration laissées au superviseur.
