# Lot 370 — A2, séquence et attente

30 octobre 2026 — branche `codex-a2-sequence-attente`, base d'intégration
`d856732411ea5ae54fa5d9cf1b1b65ddc02f947b`, non fusionnée.

**Invariant.** `donjon/contrats_sequence.py` décrit la composition bornée,
l'attente de cinq minutes en bloc, la durée interruptible et les deux minutes
à guetter une occasion. `operations.traduire/compiler/preparer`,
`Moteur.preparer`, le schéma du MJ (proposition et suite après admission de
faits), les commandes et `comprehension.plan_admis` réemploient ces contrats.
L'expansion de `voler/finesse` reste `patienter` puis déplacement discret ;
`voler/simple` n'acquiert aucune attente. Les autres opérations conservent
leurs compilateurs et leurs contrôles.

**Ce qui change.** Les branches de schéma réservées à `patienter` et
`attendre` ferment leurs paramètres : un outil, une méthode voisine, une
destination ou un champ de condition ne remplacent pas leur charge.
L'attente sans durée refuse désormais, comme celle avec durée, un outil,
une méthode autre que `simple` ou une difficulté que l'ancienne branche
ignorait. Les durées, interruptions, jets, bonus et effets des charges
valides restent inchangés. « Compris » explicite les limites de l'occasion
et distingue les deux attentes ordinaires ; les secondes transportées dans
`cible` sont déjà exprimées en durée dans le titre. L'oracle U-P `vol` est
adapté à cette précision publique uniquement : étapes, cible, méthode,
arrêt et assertions de sécurité sont conservés.

**Preuves ciblées.** Cinq nouveaux tests verts : cas historique `crypte/26`
(crochets), autre bien (bourse déclarée dans la scène), faux pendant (vol
direct), refus sans mutation des paramètres voisins et des conditions
étrangères, identité du monde après sauvegarde/recharge et du texte relu
dans la vraie boucle web/console. Comparaison des raccourcis aux étapes
explicites ; deux et cinq minutes comparées à des tranches de quinze
secondes, avec recharge à chaque tranche, état complet hors journal,
conversation et révision, scène/fiche/vue identiques. Une attente à guetter
reste une activité distincte du repos : le découpage utilise le même geste.
Le test du schéma effectivement émis contrôle aussi la suite après faits.
La première passe a révélé des erreurs dans le montage des nouveaux tests
(bien absent, clé facultative, repos substitué au guet), corrigées sans
modifier le moteur pour les faire passer ; ses bruts sont conservés.

**Mesures en cours.** Vérification finale détachée : neuf fichiers concernés
(les six fichiers de famille et voisins, plus connexion, protocole et
fournisseurs), deux travailleurs à priorité réduite, puis empreintes 2 h,
Relais, graines 1985/7/42/2024, contre la base exacte ci-dessus, cache partagé
réutilisé lorsqu'il existe. Le banc disponible ne possède pas de scénario
`crypte` ; son cas réel est exercé par les tests de partie. Résultats et
statut final attendus dans
`C:/Users/msics/donjon/artifacts/a2-sequence-attente-370/fin.json` ; fichiers
`tests-finaux.json`, `empreintes.json` et sorties texte dans le même dossier.
Les cinq nouveaux tests passent sur le code final ; les 41 tests voisins
de la première passe passent également, avant la dernière précision de texte.

**Limites.** Ce lot ne garantit ni le choix fidèle de Luna ni l'attente
jusqu'à un prédicat libre : le moteur ne sait pas promettre qu'un tiers
tournera le dos. La limite est publiée avant l'acte lourd, aucune condition
n'est matérialisée par une orientation inventée. `patienter` ne devient pas
une attente de durée variable dans une séquence. Aucun nouveau mécanisme,
revue modifiée, branchement A4/A6, passe Luna ou suite complète.
L'ancienne API simple `MJ.proposer` conserve son transport et son schéma
transitoire ; la grammaire de transport relève d'A3. Pas de recouvrement de
code identifié avec 365/369/371/372 ; `docs/etat-dev.md` reste partagé.
