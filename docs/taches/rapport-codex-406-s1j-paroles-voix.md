# Lot 406 — S1j, dits, audiences et savoir initial (première partie)

31 octobre 2026 · `codex-s1j-paroles-voix` · base exacte `integration b4130dc3`.
Code mesuré : **`914dbb07`**. Livraison partielle cohérente prévue par le brief.
Intégration `4539dd68` fusionnée sans conflit (`3ca41108`), aucun recouvrement de code.
Puis `b9bef393` (documentation seule), conflit d'état-dev résolu en conservant les deux apports.
**Lot clos sur ce périmètre ; aucun calcul restant.**

**Invariant porté.** Les registres `faits_dits` et `faits_initiaux` ne se lisent et
ne se modifient plus hors de `memoire`, hormis leur déclaration de schéma et leur
création vide générique dans `esprits`. Les vues `dits_retenus`, `faits_initiaux`
et `paroles_retenues` donnent des copies profondes pour un observateur explicite,
sans créer d'esprit, apprendre, tirer ou reconstruire une provenance absente.
Les occurrences de parole restent dans le tampon historique ; les émissions
restent sous l'autorité d'`emissions`, sans second flux de mots.

`memoire` porte les identités des faits dits, la rétention et la révision des dits,
les audiences effectivement connues, l'installation et la révision de l'ancrage
initial, la migration et la validation historiques. Les fonctions de `social`
restent des façades ; `paroles.paroles_retenues` emploie la vue spécialisée.
Entendre reste distinct de croire ; une saturation à 512 tait un fait nouveau
sans attester sa transmission. Un changement appris par le destinataire seul
rouvre son suivi. L'inventaire de départ reste silencieux, même découvert plus
tard ; son transfert appris devient une nouvelle. Clés, copies d'admission,
ordre des entrées, plafonds et crochets sont conservés.

**Contrôle et tests acquis.** Le contrôle AST de S1f accepte désormais une famille
de registres ; S1j contrôle également les suppressions et mises à jour de clés
racines. Inventaire dédié **122 → 0 expressions** (92 dans `social`, 30 dans
`esprits`), sans accès restant autorisé ; les inventaires antérieurs restent
inchangés. Contre-épreuves : clés indirectes, alias, boucles, méthodes détachées,
retours, créations et mutations. Deux créations de schéma seulement sont admises
par leur expression exacte. **235/235 tests distincts verts**, dix-sept fichiers :
dits et audiences (19), socle, localisations, savoir initial et nouvelle porte
(44, dont cinq nouveaux tests), puis onze fichiers métier voisins (172, 170,7 s).
Captures : mine 3, Josse et Lucien, puis audience du Relais avec témoin absent.
Deux minutes entières ou huit tranches avec recharges : état complet et ordre
JSON, lignes, rendu, scène et émissions identiques ; non-répétition contrôlée.
Copies imbriquées, saturation, absence d'adoption implicite et ancien registre
d'auditeurs également vérifiés.

**Empreintes : 16/16 identiques.** 2 h × quatre graines 1985/7/42/2024 ×
Relais/mine/auberge/crue, commits exacts `b4130dc3` et `914dbb07` : chronique,
mesures et état final complet identiques, sans exclusion ni plantage. Avis et
constats auxiliaires concordants : zéro avis non justifié, vingt à expliquer
de chaque côté. Les seize nuits de référence puis de branche ont été jouées
et rangées dans le cache partagé ; aucun temps comparé. Deux travailleurs au
plus, priorité réduite, étapes successives. Aucune suite complète ni Luna.
Ces empreintes précèdent la fusion du 403 ; elles ne mesurent pas cette nouvelle
intégration. Après fusion, **10/10 tests verts** (13,8 s, `1e3e378b`) : porte S1j
renforcée et audiences, dont mots effectivement émis/retenus et chaîne complète.
La dernière fusion est documentaire ; aucun code n'a changé depuis cette passe.

**Bruts.** `C:/Users/msics/donjon/artifacts/s1j-406/` : premiers tests et inventaire
avant portage, `tests-metier.json/log`, `empreintes-base.json/log`, `fin.json`,
`tests-apres-integration.json/log` et **`fin-integration.json` (`succes: true`)**.
Les scripts détachés `run406.py` et `apres406.py` et la conclusion y restent.

**Limites et suite.** L'identité vocale reste à porter : voix connues et entendues,
prétentions, imposture, noms appris, échanges retenus et leurs migrations et
validations. L'invariant complet de S1j n'est donc pas clos. Le contrôle AST est
syntaxique et local ; il ne prouve pas tous les flux interprocéduraux de Python.
L'ancienne limite de `_sait` et la rétention historique restent inchangées.
Aucun changement dans les fonctions de passage du 381 ; aucun recouvrement avec
le code du 403 (`corps`, `ecoute`), fusionné tel quel. `historique-lots.md` est
modifié uniquement par cette fusion du superviseur. Ni nouvel oubli ni nouveau
jugement social. La vérification est terminée ; la suite de S1j porte l'identité
vocale, sans présenter cette livraison comme l'invariant complet du brief.
