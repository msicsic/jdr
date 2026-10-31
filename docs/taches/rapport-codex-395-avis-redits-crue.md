# Lot 395 — provenance de l'extinction dans la capture crue 2024

Branche `codex-avis-redits-crue`, base `integration 1fd48fb5`, laptop.
**Lot terminé, non fusionné ; branche poussée.** Implémentation : `998ffc88`.
Bruts : `C:/Users/msics/donjon/artifacts/avis-redits-395/`.

**Invariant.** Une observation initiale inchangée ne constitue pas une
nouvelle. Un changement appris rend son état racontable ; une nouvelle vue
du seul locuteur ne rouvre pas les destinataires déjà servis.

**Diagnostic et preuve.** La capture crue à 140 précède `faits_initiaux`.
Brune porte la torche éteinte, avec une croyance `vu` datée de 140 ; le
chargement du 360 ancre donc `allume=false` dans sa provenance initiale.
`social.nouvelles` n'offre aucune extinction : la migration prudente du 360
ne reconstruit pas le passé absent. La chronique atteste pourtant Brune
allumant la torche à **97**, l'éteignant à **104**, puis annonçant son
extinction à **Aubin à 122**. Aubin croit encore l'allumage vu à 100 ; Ilse
et Gorm (`marchand`) celui vu à 102. Le registre de Brune conserve Aubin
comme destinataire de l'extinction ; il ne porte pas les deux autres.
Preuve : `provenance.json` (croyances, provenance, audience, chronique, empreinte).

**Portage de la scène.** Le test restitue par `croire` la vue allumée
antérieure attestée à 97, puis laisse `percevoir` constater l'état actuel
éteint à 140. Il vérifie le silence initial, la nouvelle ensuite disponible,
l'état matériel conservé et le suivi d'Aubin toujours fermé. Cette prémisse
est appliquée une fois avant chacun des deux parcours ; aucune confidence
n'est injectée. Aucun code du jeu modifié ni registre ajouté ; besoins,
liens, audience et jets restent ceux de la capture compressée intacte.

**Isolation autorisée par l'utilisateur.** Avec les profils d'origine,
Brune poursuit des buts concurrents de souci spontané, sans transmission.
L'utilisateur autorise l'isolation positive comme les lampes du 375 : `secours_spontane=False`
déclare `altruisme=empathie=0` dans les profils de la copie, sans changer
besoins, liens, audience ou jets. Le commentaire du test cite la décision
du 395 et les buts concurrents. **L'assertion de transmission reste intacte.**
Un quatrième test garde les profils d'origine et vérifie l'absence de redite
sans rallumage appris par l'auditeur. README et tests documentent ces prémisses.
Le harnais historique minier du 375 reste limité à son épreuve existante.

**Validation finale.** **4/4 avis verts**, 374,342 s, sources stables.
Scène isolée : une transmission de Brune à Ilse à **141** (instant 84668),
aucun rallumage ni redite. Profils d'origine : zéro transmission, zéro
rallumage ; le contrôle négatif passe sans démontrer une émission.
Mine : Josse transmet les deux lampes distinctes à Lucien à 76 et 77.
Monde entier, regard, paroles entendues et scène sont conservés après
rechargement et entre laps entier/découpé. Les **13 assertions originales
restent intactes**, dix ajoutées. Empreintes du test et de la capture vérifiées.

Les neuf fichiers du 360 et `test_deja_dit` : **97 tests, 95 verts, deux
échecs, zéro erreur/saut**, 972,454 s. Les deux rouges de `ChaineTests`
(`test_agendas_socle`) sont **reproduits sur la base native `1fd48fb5`** :
`test_achat_apres_abandon_conserve_la_piece_due_puis_la_solde` reçoit
(99, 1) au lieu de (100, 0) ; `test_tache_payee_acceptee_puis_abandonnee`
reçoit (80, 20) au lieu de (100, 0). Le fichier de base donne les mêmes deux
rouges sur six tests. Ses sources et les 129 modules du jeu sont inchangés.
Ces défauts préexistants restent hors périmètre ; aucun test relâché.

Bruts : `avis.json`, `parcours-test_*.json`, `tests-360.json`,
`agendas-base-1fd48fb5.json`, `conclusion.json`. **`fin.json ok=false` est
conservé** : il reflète les deux rouges voisins, pas un échec des avis.
Deux travailleurs au plus, priorité réduite, calcul final des avis détaché.
Aucun banc, Luna ou suite complète ; aucune relance des campagnes achevées.

**Limites.** La transmission spontanée dans la nuit réelle n'est pas prouvée.
Aucune reconstruction générale des provenances historiques, ni garantie
universelle sur les nuits ou les boucles n'est déduite de ces captures.
