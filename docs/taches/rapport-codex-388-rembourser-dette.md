# Lot 388 — Rembourser volontairement une dette en pièces

Branche `codex-rembourser-dette`, base `integration ea3c70e0`, laptop.
**Implémentation livrée ; vérification finale en cours, non fusionnée.**

**Invariant.** Le remboursement volontaire du joueur et celui du PNJ utilisent
`biens.rembourser_dette` : dette existante du débiteur, montant entier positif
au plus égal au dû, créancier présent et capable d'entendre, fonds suffisants.
Chaque refus décrit sa cause et son `attendu`, avant tout transfert. Le montant
vide règle tout le dû envers ce destinataire ; les lignes anciennes passent
d'abord. Le reste demeure dans `data["dettes"]`, sans nouveau registre d'esprit.

**Chaîne commune.** `_verser_dette` partage avec le règlement réclamé le transfert,
les comptes et les souvenirs. Le créancier reçoit l'épreuve relationnelle
existante `dette_honoree`, proportionnée aux pièces effectivement remises ;
les restes distincts différencient deux versements d'une même somme sur plusieurs
lignes. Le validateur de sauvegarde admet désormais Corvus comme débiteur.
`comptes_joueur` affiche aussi ses dettes dans la fiche.

Le contenu `rembourser {montant}` entre dans l'union des paroles, son sens et
la revue de fidélité. U-C le traite comme lourd par défaut : préparation sur
copie, « Compris » avec montant et créancier, puis confirmation avant publication.
G17 formule et enregistre la réponse comptable ; une annulation ne paie pas.
Le temps seul ne débite jamais Corvus. Aucun formulaire web ni menu ajouté.

Le planificateur propose le geste `rembourser` sur le palier permanent de
l'argent : coût du trajet et des pièces contre le prix moral de garder le dû,
selon l'honnêteté existante. La position visée est crue ; le geste revalide
présence, audience, fonds et dette réels, puis enregistre ses mots par la voie
commune des paroles PNJ. Plus de dette ou de fonds : plus de versement candidat.
Les réclamations automatiques entre PNJ conservent leur voie actuelle ; le
remboursement spontané est désormais choisi par le planificateur.

**Épreuves.** Le nouveau fichier couvre total à Brune, partiel à Gorm, plusieurs
lignes, aperçu/annulation, dépassement, dette inconnue, absence, inaudibilité,
manque de fonds, absence de débit au passage du temps, PNJ honnête sans
réclamation, déplacement et remboursement partiel sans répétition. Il contrôle
bourses, dettes, paroles, épreuve relationnelle et vues après recharge, ainsi
que les mêmes comptes et émissions après un laps entier ou découpé.
Le premier passage a révélé le contrat de sauvegarde manquant, puis deux erreurs
de montage des tests (champs de transport et case hors sol), corrigées.
Les premiers parcours joueur, U-C et refus passent ; le résultat final fait foi.

Onze fichiers ciblés sont lancés, sans suite complète, puis une reprise des
trois fichiers directement concernés par les derniers changements. Le lanceur
enchaîne les bancs de branche Relais et auberge, 4 h × quatre graines, deux
travailleurs à priorité réduite, puis **une seule passe Luna ChatGPT** sur
`tests/data/bancs/rembourser.json`, exclusivement sur copies temporaires.
Commandes exactes, journaux et résultats :
`C:/Users/msics/donjon/artifacts/rembourser-388/` ; fichier de fin écrit en dernier :
`fin-verification.json`. Ne pas déclarer la vérification acquise avant lecture
de `tests-cibles.json`, `tests-finaux.json`, des bancs et du fil Luna.

**Limites.** Aucun résultat de performance ni absence générale de régression
affirmé avant la fin des calculs. Le remboursement peut attendre les besoins
plus urgents du PNJ. Il n'efface aucun tort indépendant et ne crée pas de prêt
monétaire nouveau. Fusion et vérification d'intégration laissées au superviseur.
