# Lot 388 — Rembourser volontairement une dette en pièces

Branche `codex-rembourser-dette`, base `integration ea3c70e0`, laptop.
**Terminé, non fusionné. Un échec préexistant demeure dans les tests ciblés.**

**Invariant.** Joueur et PNJ utilisent `biens.rembourser_dette` : dette connue
du débiteur, entier positif au plus égal au dû, créancier présent et capable
d'entendre, fonds suffisants. Chaque refus a son `attendu`, avant transfert.
Un montant vide règle tout le dû envers ce destinataire, les lignes anciennes
d'abord ; le reste demeure dans `data["dettes"]`, sans registre supplémentaire.
`_verser_dette` partage avec le règlement réclamé transfert, comptes et souvenirs.
La remise donne au créancier l'épreuve existante `dette_honoree`, à hauteur des
pièces versées ; les restes distinguent deux versements identiques sur plusieurs
lignes. Sauvegarde et `comptes_joueur` admettent désormais Corvus débiteur.

Le contenu `rembourser {montant}` rejoint l'union des paroles et la fidélité.
U-C prépare sur copie, montre « Compris » avec montant et créancier, attend
confirmation ; G17 enregistre les mots comptables avant affichage. Annuler ou
laisser passer le temps ne paie pas. Aucun menu ni formulaire ajouté.
Le planificateur compare pièces et trajet au prix moral de garder le dû, sur
le palier permanent de l'argent. Il vise la position crue ; le geste revalide
le réel, conserve le récapitulatif visible du versement et enregistre sa parole.
Une dette soldée ou une bourse vide ne produit plus de versement candidat.

**Tests : 97 réussites / 98, sur onze fichiers, bilan consolidé des reprises.**
Les huit nouveaux tests passent : total à Brune, partiel à Gorm, plusieurs
lignes, refus distincts sans mutation, aperçu/annulation sans effet, PNJ honnête
sans réclamation, déplacement et absence de second versement sans fonds.
Bourses, dettes, paroles entendues, épreuve relationnelle et vues sont contrôlées
après recharge ; comptes et émissions concordent entre laps entier et découpé.
Les tests d'échéance observent désormais la naissance de la dette avant le
départ spontané du PNJ, puis sa remise effective. Les scènes isolent la créance
testée de la dette personnelle de scénario, qui déclenchait une vente concurrente
légitime. Le seul rouge, le secours de Gaspard
(`test_scene_exacte_le_secours_differe_le_pret_jusqu_au_calme_percu`), se reproduit
sur une archive de la base `ea3c70e0` ; il reste hors lot. Aucune suite complète.

**Bancs :** Relais et auberge, 4 h × graines 1985/7/42/2024, deux travailleurs
réduits, huit nuits achevées ; zéro usurpation, zéro bascule d'état répétée.
Maximum de passages par PNJ/heure : 10 au Relais, 24 à l'auberge ; trois avis
redits à l'auberge. Ces nuits ne déclenchent aucun remboursement : la preuve
de non-répétition du versement vient des tests ciblés. Durées par nuit :
28,41–37,20 s / 50,09–74,19 s ; aucun gain comparatif de performance affirmé.

**Luna : une passe sur copies**, `tests/data/bancs/rembourser.json` : quatre
appels, 20,07 s au total, zéro refus, repli, erreur ou échec de recharge.
Brune reçoit les quatre pièces après confirmation ; Gorm reçoit deux pièces
et dit les trois restantes. Les aperçus conservent les montants demandés.

**Limites et livraison.** Le remboursement peut attendre un besoin plus urgent
ou une autre démarche financière ; il n'efface aucun tort indépendant et ne
crée pas de prêt monétaire nouveau. Les réclamations entre PNJ gardent leur voie
actuelle. Fusion et vérification d'intégration restent au superviseur.
Bruts, commandes, fil Luna et preuve du rouge hérité :
`C:/Users/msics/donjon/artifacts/rembourser-388/` ; bilan final
`fin-conclusion.json`. Les anciens fichiers rouges sont conservés.
