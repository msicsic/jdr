# Lot 345 — G16, information parlée

Branche `codex-g16-information`, **terminée, non fusionnée**, base exacte
`origin/integration 3e3afe25c1e1ef377472d7714d7e499c0f72da08`.
Code moteur `8a7ac3a` inchangé depuis la validation ; clôture des tests et des
documents poussée. Aucun calcul actif.

**Invariant.** `paroles.preparer_parole` conserve les issues typées d'identité,
de ressource et de localisation, dont la croyance datée du locuteur.
`informations_parlees.formuler` en tire les mots sans relire une position
réelle, sans geste ni émotion ajoutés. Un nom revendiqué reste une déclaration ;
doute, imposture démasquée, refus de nom et réponses négatives sont formulés
par le moteur. Une parole enregistrée n'établit pas la vérité de son contenu.

**Contrat commun.** `repliques_moteur` partage l'admission G17 : composition
ordonnée des opérations, émission G15 sur copie, réception des présentations
par les auditeurs, transaction, scellement et contrôle exact avant publication.
Information et compte peuvent appartenir à la même réplique. `mj` et
`consentement` reprennent ces mots ; `narration.consigner` contrôle ordre et
multiplicité. Les contenus résiduels gardent leurs contrôles : conversation
ouverte, avis, passage gratuit et rappels non exacts. Ni `jeu.py`, ni `tui.py`,
ni les règles de croyance ou les mécaniques sociales ne changent.

**Preuves sans réseau.** Sept nouveaux tests contrôlent console, monde, mots,
conversation, scène et rendu après recharge : Ilse dans `soir-noir`, imposture
Brune, deux refus de nom, ressources positives et négatives sans transfert,
deux localisations crues fausses, composition avec remboursement et propos
résiduel. Modification, omission et double publication sont refusées.
**265 tests consolidés / 18 fichiers : quatre assertions préexistantes, zéro
erreur ni saut, aucun incident nouveau.** G16 7/7, G15 11/11, G17 11/11,
noms 33/33, narration 31/31 et consentement 9/9 verts. Passe initiale
770,603 s ; reprise des quatre fichiers concernés, 60 tests, 306,030 s ;
deux méthodes de passage reprises vertes, 42,121 s. Les tests observent la
préparation réelle sans fabriquer d'appel modèle et confirment explicitement
les actes lourds. Le passage gratuit conserve ses mots audités et son repli.

**Attribution des réserves.** Trois méthodes sur la base exacte, 12,069 s :
persuasion Hugues/Anselme et trois assertions de faisabilité dans
`test_luna_noms`. Les quatre assertions **et leurs sorties sont identiques**
à la branche hors chemins locaux ; oracles inchangés. Aucun correctif social
ou de faisabilité ajouté. Bruts rouges et erreur du premier lanceur de
référence conservés ; import du paquet `tests` corrigé dans ce lanceur seul.
Aucune suite complète ni banc PNJ ; deux travailleurs réduits au plus.

**Luna, une seule passe.** `soir-noir`, `ressources`, `noms-dialogue` :
**28 appels** (11/6/11), zéro repli, refus ou erreur technique/recharge.
Sept tours d'information typée : une compilation et une revue de fidélité,
**zéro rédaction supplémentaire et zéro audit narratif**. Six sont exécutés
sans réponse perdue ; l'imposture attend la confirmation du joueur dans le
script, son exécution étant couverte sans réseau. Témoin historique `cdaf371`
relu du cache sans appel : 51 appels (22/12/17). Aucune attribution causale
face à la base d'intégration, ni comparaison de vitesse revendiquée.

**Limites et livraison.** Le script actuel `noms-dialogue` ne pose pas de
question de localisation : les deux scènes simulées couvrent cette voie.
La sémantique libre reste sous les contrôles des voies non portées.
Recouvrements : **`paroles.py` avec 341**, **`narration.py` avec 343** et raccords
G17 communs. Bruts `C:/Users/msics/donjon/artifacts/g16-345/` :
`tests-consolides.json`, `analyse-cloture.json`, `reference.json`,
`luna-mesures.json`, **`fin-cloture.json` avec réserves antérieures**.
Le premier `fin-validation.json` rouge est conservé. Aucune seconde passe Luna.
