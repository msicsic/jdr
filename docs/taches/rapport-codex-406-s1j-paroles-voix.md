# Lot 406 — S1j, dits, audiences et savoir initial (première partie)

31 octobre 2026 · `codex-s1j-paroles-voix` · base exacte `integration b4130dc3`.
Code mesuré : **`914dbb07`**. Livraison partielle cohérente prévue par le brief.
Intégration `4539dd68` fusionnée sans conflit (`3ca41108`), aucun recouvrement de code.

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

**Vérification détachée en cours.** Empreintes 2 h × quatre graines
1985/7/42/2024 × Relais/mine/auberge/crue, sur les commits
exacts `b4130dc3` et `914dbb07`, avec cache partagé. Deux travailleurs au plus,
priorité réduite, étapes successives. Aucune suite complète ni Luna.
Résultats attendus dans `C:/Users/msics/donjon/artifacts/s1j-406/` :
`tests-metier.json/log`, `empreintes-base.json/log`, puis `fin.json`. Ensuite,
`apres406.py` lance en série la porte S1j renforcée et les audiences après fusion
(copies, schéma, mots effectivement émis/retenus, chaîne complète).
**`fin-integration.json` est le marqueur final**, écrit après
`tests-apres-integration.json/log`. Les premiers résultats et l'inventaire avant
portage y sont conservés. L'identité des seize nuits n'est pas encore acquise ;
ces empreintes précèdent la fusion et ne mesurent pas l'intégration nouvelle.

**Limites et suite.** L'identité vocale reste à porter : voix connues et entendues,
prétentions, imposture, noms appris, échanges retenus et leurs migrations et
validations. L'invariant complet de S1j n'est donc pas clos. Le contrôle AST est
syntaxique et local ; il ne prouve pas tous les flux interprocéduraux de Python.
L'ancienne limite de `_sait` et la rétention historique restent inchangées.
Aucun changement dans les fonctions de passage du 381 ; aucun recouvrement avec
le code du 403 (`corps`, `ecoute`), fusionné tel quel. `historique-lots.md` est
modifié uniquement par cette fusion du superviseur. Ni nouvel oubli ni nouveau
jugement social. Branche livrée avec calcul détaché ; relire le marqueur final
avant de clore sa vérification.
