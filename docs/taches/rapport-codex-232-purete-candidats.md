# Lot 232 — clôtures de service après le choix

Branche `codex-purete-candidats`, non fusionnée ; base `adb52c4`
de l'intégration. Aucun Luna, aucune modification des fichiers réservés aux
lots 233–235. Les calculs emploient au plus deux processus à priorité réduite.

**Invariant et correction.** `biens.services_proteges` calculait les
conditions protégées et supprimait simultanément les traces finies dans
`data.services_rendus`. Cette suppression est désormais proposée dans un
registre temporaire, hors de `data`. `planification.vues_du_choix` ouvre
`biens.clotures_services_du_choix` : publication après la sortie réussie du
choix, de son contrôle de pureté et des transitions d'agenda ; un choix
imbriqué transmet au parent et toute interruption abandonne ses clôtures.
La lecture hors choix, notamment le devis isolé, n'écrit plus. Les critères
de cessation et la valeur renvoyée restent identiques, sans exception de
personnage, scénario ou nature de service.

**Diagnostic.** La base demandée contient les lots 218 et 230, postérieurs
au moteur historique `4306c14` du lot 231. Les deux trajectoires sont donc
distinguées dans les bruts. Sur `adb52c4`, mine 42 achève les huit heures ;
une suppression est observée à 439, par `menager_flamme` pour Gaspard
(service d'allumage du poêle à Josse).
Rixe 42 achève également les huit heures sur cette base, avec deux
lectures supprimant la trace torche/marchand de Brune (79 : devis sur
copie ; 80 : `menager_flamme`).
Sur `4306c14`, l'arrêt mine est reproduit au pas 415 (copie de travail à
418) : Gaspard, recours d'empathie, `_entrees_communes` appelle
`services_proteges` qui retire la trace poêle/Josse de `services_rendus`.
Rixe s'arrête au pas 350 (copie à 351) : Aubin, candidat `voir`, même
chaîne, suppression de la trace brasero/marchand. Aucun autre champ modifié
par ces lectures ; les deux arrêts sont bien ceux du lot 231.

**Vérifications.** 22 tests ciblés verts, quatre fichiers, 90,903 s,
dont cinq nouveaux : captures historiques mine/rixe, autre service de
serrure, lecture et devis isolés purs, publication au choix réussi,
imbrications interrompues et rejet par le témoin de pureté. Monde,
`regarder`, scène perçue et laps 2 min / 1 + recharge + 1 contrôlés.
Mine et rixe 42 corrigées : huit heures achevées avec `VERIFIER` et
spatial 0,2, mesures et mondes finaux complets identiques à la base
actuelle (comparaison JSON structurelle). **12/12 paires d'empreintes 2 h
identiques** contre `integration adb52c4`, Relais/mine/rixe × graines
1985/7/42/2024 : chronique, mesures, état final complet, zéro plantage.
Les douze références manquantes ont été jouées une fois et rangées en cache.
**Suite complète unique : 2 526 tests / 292 fichiers, 2 366,049 s,
quatre échecs, zéro erreur**, suite non verte. Lucien (`3 != 1`) et deux
MiMo (`6 != 5`) correspondent exactement aux traces préexistantes du
lot 230 sur `1e09926`, réutilisées sans rejeu. Le quatrième, compteur de
torche hameau 1985, est reproduit sur `adb52c4` après la suite (un seul
test, 9,414 s) : même Brune/Ilse, réussite 3188, perte 3615, même cause
et mêmes croyances. Aucun oracle modifié, aucun nouvel échec identifié.
Créneau de 45 min dépassé par les reproductions historiques et la suite
complète ; aucune seconde suite, aucun banc supplémentaire hors brief.

**Limites.** La correction garantit que cette lecture ne modifie ni le monde
ni un esprit. Elle ne rend pas transactionnelles toutes les écritures du
jeu et ne prouve pas l'absence universelle d'une autre mutation candidate ;
le contrôle `VERIFIER` demeure actif. Une trace devenue caduque lors d'un
devis isolé demeure stockée jusqu'à sa lecture dans un choix réussi, mais
elle n'est plus renvoyée comme protégée. Pas de migration de sauvegarde.
La perte de torche déjà présente sur la base reste à traiter séparément.

Bruts : `C:/Users/msics/donjon/artifacts/purete-232/`.
