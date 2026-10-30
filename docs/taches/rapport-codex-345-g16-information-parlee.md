# Lot 345 — G16, information parlée

Branche `codex-g16-information`, **non fusionnée**, base exacte
`origin/integration 3e3afe25c1e1ef377472d7714d7e499c0f72da08`.
Code livré ; **validation finale détachée en cours**. Ne pas déclarer le lot
validé avant lecture de `C:/Users/msics/donjon/artifacts/g16-345/fin-validation.json`.

**Invariant et fonctions.** `paroles.preparer_parole` conserve les issues
typées d'identité, de ressource et de localisation, dont la croyance datée
du locuteur. `informations_parlees.formuler` en tire les mots sans relire
une position réelle, sans geste ni émotion ajoutés. Un nom revendiqué reste
une déclaration ; le locuteur qui doute ou démasque le dit. Le refus de se
nommer et les réponses négatives sont eux aussi écrits par le moteur.

`repliques_moteur` extrait et partage l'admission G17 : composition ordonnée
des opérations, émission G15 sur copie, réception des présentations par les
auditeurs, transaction, scellement et contrôle exact avant publication.
Information et compte peuvent appartenir à la même réplique. `mj` et
`consentement` reprennent ces mots ; `narration.consigner` en contrôle l'ordre
et la multiplicité. Les autorisations résiduelles gardent rédaction et audit :
propos ouverts, avis et autres voies non portées. Les règles sociales et de
croyance, `jeu.py` et `tui.py` ne sont pas modifiés.

**Preuves sans réseau.** Sept nouveaux tests passent par la console réelle,
puis contrôlent monde, mots, conversation, scène et rendu après recharge :
Ilse dans `soir-noir`, imposture Brune, deux refus de nom, ressources positives
et négatives sans transfert, deux localisations crues fausses, composition avec
remboursement et propos résiduel. Une contre-épreuve refuse modification,
omission et double publication. Précontrôle intermédiaire : **7/7**, comptes
**11/11**, noms **33/33**, dialogues **18/18**. La validation du code final porte
sur **18 fichiers ciblés**, deux travailleurs réduits au plus, sans suite
complète ni banc PNJ. Les anciens tests qui lisaient le deuxième appel lisent
désormais la préparation réellement observée, sans fabriquer d'appel modèle.
Les tests de parcours à effet lourd confirment explicitement leur action.

**Luna, une seule passe achevée.** `soir-noir`, `ressources`, `noms-dialogue` :
**28 appels** (11/6/11), zéro repli, refus technique ou erreur de recharge.
Sept tours d'information typée : une compilation et une revue de fidélité,
**zéro rédaction supplémentaire et zéro audit narratif**. Six sont exécutés ;
l'imposture reste en attente de confirmation dans le script, son exécution
étant vérifiée sans réseau. Aucun silence substitué aux six réponses exécutées.
Référence **historique** `cdaf371`, relue du cache sans appel : 51 appels
(22/12/17). Ce témoin ancien ne mesure pas l'effet causal de G16 face à sa
base d'intégration ; aucune comparaison de vitesse revendiquée.

**Réserves et reprise.** La première sélection intermédiaire (140 tests)
conserve ses résultats rouges : attentes de rédaction périmées, imports pris
pendant le portage d'un test, et incidents antérieurs. L'échec de persuasion
Hugues/Anselme est reproduit sur la base exacte (un test, 2,338 s), sans modifier
son oracle. Le calcul final rejoue aussi sur cette base les deux méthodes de
faisabilité signalées par `test_luna_noms`. Il écrit les traces et empreintes
dans `tests-finaux.json`, `reference.json` et `luna-mesures.json`, puis le fichier
de fin **en dernier**. Il reste à lire ces résultats, attribuer tout incident,
puis clôturer ce rapport et l'état de développement. Aucune seconde passe Luna.

Limites : conversation ouverte et rappels non exacts restent audités ; le
script actuel `noms-dialogue` ne pose pas de question de localisation, couverte
ici par les deux scènes simulées. Recouvrements : **`paroles.py` avec 341**,
**`narration.py` avec 343**, ainsi que les raccords G17 communs.
Bruts : `C:/Users/msics/donjon/artifacts/g16-345/` ; lanceur et copie isolée
de la référence sous `artifacts/g16-345/` dans ce worktree.
