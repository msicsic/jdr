# Lot 404 — S1h, preuves d'eau et statuts sourcés

31 octobre 2026 · `codex-s1h-eau-statuts` · base exacte `integration d451a4ce`.
Code mesuré : **`88f4f9ab`**. **Lot clos, non fusionné ; aucun calcul restant.**

**Invariant et code.** Les mesures d'eau (hauteur, niveau, pente, repère), les avis
reçus et les statuts passent par les vues profondes de `memoire` : `mesure_eau`,
`mesures_eau`, `avis_eau`, `statuts_connus`. `esprits.croyance` protège également
ces trois familles ; `prevision` rend une copie même pour un avis qualitatif.
Aucune consultation ne crée d'esprit, ne complète une preuve depuis le réel,
ne réapprend une information ni ne relance un jet. Zéro, faux et liste de statuts
vide restent des preuves négatives, distinctes d'une absence de preuve.

`memoire.prevision_propre/prevision/recevoir_prevision` et `recevoir_statuts`
portent les politiques historiques ; les anciennes fonctions restent façades.
La prévision propre conserve sa borne et la qualité de sa preuve la plus faible.
La réception des avis conserve date, poids × conviction, arrondi à douze décimales,
égalité refusée sauf départage de dispute, rang, chronique puis reconsidération.
Les statuts conservent date puis poids × conviction, égalité admise et validation.
L'admission commune remplace les cellules et retire durablement les avis antérieurs
à un constat propre étayé ; l'observation d'eau garde le même calcul de repère.
Stockage, ordre et sérialisation historiques inchangés ; aucun registre ajouté.

Lecteurs portés : `eau.eau_crue/borner/estimation/observer`, prévisions d'`esprits`
et cause de détresse liée à l'eau. Le contrat commun protège aussi les lecteurs
existants d'avis, de disputes et de statuts qui passent déjà par les façades.
Aucune fonction de passage du 381 ni terminal de remboursement du 399 modifiés.
Recouvrement possible avec 403 : modules et tests communs, sans correction de
ses rouges ni modification de leur scénario. `historique-lots.md` reste intact.

**Inventaire et tests.** Inventaire AST fermé : **168 → 129 expressions**, aucune
addition. Les contre-épreuves couvrent clés indirectes, alias, boucles et mutations
des trois familles. Le contrôle historique des statuts admet seulement les fonctions
de schéma/vue/admission de `memoire`, sans exemption globale du module.
**141/142 tests verts**, seize fichiers distincts, dernières passes consolidées,
aucun échec ni saut, une erreur héritée. Porte : 36/36 (71,1 s), dont quatre nouveaux
tests S1h ; quatorze fichiers complémentaires : 110 tests (558,4 s) ; après correction
du contrôle AST, statuts : 6/6 (3,7 s). Copies imbriquées, preuve négative, retrait
durable d'un avis et pureté vérifiés. Deux captures historiques du 124 (crue 500,
Gorm ; crue 2024, Ilse) : dix minutes entières ou dix fois une minute avec recharges ;
état complet et ordre JSON, lignes, rendu, scène et registre des paroles identiques
après recharge. Les statuts vérifient aussi scène et paroles au Relais et à la mine.

Le seul rouge, `test_eau.PnjTests.test_l_eau_qui_monte_fait_fuir_vers_la_galerie`,
est reproduit isolément sur la **base exacte `d451a4ce`** : même `TypeError` à la
ligne 257, car l'estimation d'Ilse vaut `None` au lieu du triplet attendu. Oracle
intact ; aucune correction de comportement revendiquée pour cette erreur.

**Empreintes : 16/16 identiques.** **2 h × quatre graines 1985/7/42/2024 ×
Relais/mine/auberge/crue**, base exacte `d451a4ce`, branche `88f4f9ab` : chronique,
mesures et état final complet identiques, sans exclusion ni plantage. Constats et
avis auxiliaires identiques : zéro non justifié, vingt à expliquer de chaque côté.
Les seize nuits de référence puis de branche ont été rangées dans le cache partagé ;
deux travailleurs réduits au plus, aucun temps comparé. Pas de suite complète ni Luna.

**Bruts et limites.** `C:/Users/msics/donjon/artifacts/s1h-404/` : `tests-porte.json`,
`tests-cibles.json/log`, `empreintes-base.json/log`, `run404.py`, `fin.json`,
`tests-statuts-corriges.json/log`, `attribution-eau-base.log`, `conclusion.json`.
`fin.json` conserve le code rouge initial ; `conclusion.json` consolide la correction
du contrôle et l'attribution. `origin/integration d451a4ce` n'a pas avancé à la clôture.
Le moteur mesuré est inchangé depuis `88f4f9ab` ; seule la correction du contrôle AST
et la documentation suivent. Le contrôle reste syntaxique/local, sans preuve exhaustive
des flux interprocéduraux Python. Pas de nouvelle règle d'oubli ou de jugement social.
